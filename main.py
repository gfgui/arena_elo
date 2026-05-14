import random
import matplotlib.pyplot as plt
import seaborn as sns
from models.player import Player
from models.challenge import Challenge
from engine.elo_engine import EloEngine

def simulate_attempt(engine: EloEngine, player: Player, challenge: Challenge) -> int:
    """
    Simulates if the student gets it right or wrong based on their real/hidden attributes.
    """
    # What is the REAL chance of success? 
    real_success_chance = engine.calculate_expectation(player.real_skill, challenge.real_difficulty)
    
    # Roll a dice between 0.0 and 1.0
    dice_roll = random.random()
    
    # If the dice roll is less than the chance, it's a success (1). Otherwise, failure (0).
    win = 1 if dice_roll <= real_success_chance else 0
    return win

def generate_players(count: int) -> list[Player]:
    """
    Generates players with real skills ranging from 800 (beginner) to 2200 (expert).
    """
    return [
        Player(
            player_id=i,
            name=f"Student_{i}",
            initial_rating=1500,
            real_skill=random.randint(800, 2200)
        ) for i in range(1, count + 1)
    ]

def generate_challenges(count: int) -> list[Challenge]:
    """
    Generates challenges with varying real difficulties across different topics.
    """
    topics = ["Basic Python", "Fractions", "Geometry", "Logic"]
    return [
        Challenge(
            challenge_id=j,
            topic=random.choice(topics),
            initial_rating=1200,
            real_difficulty=random.randint(800, 2200)
        ) for j in range(1, count + 1)
    ]

def select_adaptive_challenges(player: Player, challenges: list[Challenge], quantity: int, exploration_rate: float = 0.3) -> list[Challenge]:
    """
    ε-greedy matchmaking: explores random challenges some of the time,
    and adaptively selects challenges the rest.
    """
    explore_count = int(quantity * exploration_rate)
    exploit_count = quantity - explore_count
    
    # EXPLORE: Random challenges for diversity and calibration
    explored = random.sample(challenges, min(explore_count, len(challenges)))
    
    # EXPLOIT: Challenges closest to the player's current rating
    jitter = random.uniform(-100, 100)
    target_rating = player.rating + jitter
    
    sorted_candidates = sorted(
        challenges, 
        key=lambda ch: abs(ch.rating - target_rating)
    )
    
    explored_ids = {ch.challenge_id for ch in explored}
    exploited = []
    for ch in sorted_candidates:
        if ch.challenge_id not in explored_ids:
            exploited.append(ch)
            if len(exploited) >= exploit_count:
                break
    
    selected = explored + exploited
    random.shuffle(selected)
    return selected

def calculate_mae(entities: list, attr_real: str, attr_estimated: str) -> float:
    """Calculates Mean Absolute Error between real and estimated ratings."""
    if not entities:
        return 0.0
    total_error = sum(abs(getattr(e, attr_real) - getattr(e, attr_estimated)) for e in entities)
    return total_error / len(entities)

def calculate_rmse(entities: list, attr_real: str, attr_estimated: str) -> float:
    """Calculates Root Mean Square Error between real and estimated ratings."""
    if not entities:
        return 0.0
    total_sq_error = sum((getattr(e, attr_real) - getattr(e, attr_estimated)) ** 2 for e in entities)
    return (total_sq_error / len(entities)) ** 0.5

if __name__ == "__main__":
    # 1. Instantiate the Engine
    engine = EloEngine()

    # 2. Generate players and challenges
    player_count = 1000
    challenge_count = 500
    
    players = generate_players(player_count)
    challenges = generate_challenges(challenge_count)

    print(f"Arena initialized with {len(players)} players and {len(challenges)} challenges.")

    # 3. Create ANCHOR challenges
    # In a real system, these are pre-calibrated benchmark exercises
    # with known difficulty (e.g., standardized test items).
    # We anchor ~10% of challenges to their real difficulty.
    anchor_count = max(1, challenge_count // 10)  # 50 anchors
    anchor_challenges_list = random.sample(challenges, anchor_count)
    anchor_map = {ch.challenge_id: ch.real_difficulty for ch in anchor_challenges_list}
    
    # Set anchor challenge ratings to their real difficulty immediately
    for ch in anchor_challenges_list:
        ch.rating = ch.real_difficulty
    
    print(f"Anchored {anchor_count} challenges to their real difficulty (benchmark items).")

    # 4. Multi-Round Simulation with MLE recalibration
    num_rounds = 10
    interactions_per_round = 50
    total_per_player = num_rounds * interactions_per_round
    total_interactions = len(players) * total_per_player
    
    print(f"Starting multi-round simulation: {num_rounds} rounds x {interactions_per_round} interactions/player")
    print(f"Total interactions: {total_interactions}")

    for round_num in range(1, num_rounds + 1):
        print(f"\n--- Round {round_num}/{num_rounds} ---")
        
        random.shuffle(players)
        
        for player in players:
            selected_challenges = select_adaptive_challenges(
                player, challenges, interactions_per_round, exploration_rate=0.3
            )
            
            for challenge in selected_challenges:
                result = simulate_attempt(engine, player, challenge)
                engine.process_result(player, challenge, result)
                player.record_rating()
        
        # Metrics after Elo updates
        player_mae = calculate_mae(players, "real_skill", "rating")
        challenge_mae = calculate_mae(challenges, "real_difficulty", "rating")
        player_bias = sum(p.rating - p.real_skill for p in players) / len(players)
        print(f"  Player MAE: {player_mae:.1f}  |  Challenge MAE: {challenge_mae:.1f}  |  Bias: {player_bias:+.1f}")
        
        # MLE recalibration with anchors
        print("  Running anchored MLE recalibration...")
        engine.recalibrate_mle(players, challenges, anchor_challenges=anchor_map, iterations=50)
        player_mae_post = calculate_mae(players, "real_skill", "rating")
        print(f"  -> Post-MLE Player MAE: {player_mae_post:.1f}")

    print("\n\nSimulation completed!")

    # 4. Final Convergence Metrics
    print("\n" + "=" * 60)
    print("  FINAL CONVERGENCE METRICS")
    print("=" * 60)
    
    player_mae = calculate_mae(players, "real_skill", "rating")
    player_rmse = calculate_rmse(players, "real_skill", "rating")
    challenge_mae = calculate_mae(challenges, "real_difficulty", "rating")
    challenge_rmse = calculate_rmse(challenges, "real_difficulty", "rating")
    
    print(f"  Player  MAE:  {player_mae:.1f} points  |  RMSE: {player_rmse:.1f}")
    print(f"  Challenge MAE: {challenge_mae:.1f} points  |  RMSE: {challenge_rmse:.1f}")
    
    player_bias = sum(p.rating - p.real_skill for p in players) / len(players)
    challenge_bias = sum(c.rating - c.real_difficulty for c in challenges) / len(challenges)
    print(f"  Player  Bias: {player_bias:+.1f} (negative = underestimating)")
    print(f"  Challenge Bias: {challenge_bias:+.1f}")
    print("=" * 60)

    # 5. Sample Results
    print("\n--- Sample Player Results ---")
    for p in random.sample(players, 5):
        gap = p.rating - p.real_skill
        print(f"{p}  |  Gap: {gap:+.0f}")
    
    print("\n--- Sample Challenge Calibration ---")
    for c in random.sample(challenges, 5):
        gap = c.rating - c.real_difficulty
        print(f"{c}  |  Gap: {gap:+.0f}")
    
    # 6. Error Distribution
    print("\n--- Error Distribution (Players) ---")
    errors = [abs(p.rating - p.real_skill) for p in players]
    errors.sort()
    print(f"  Within  50 pts: {sum(1 for e in errors if e <= 50):>4}/{player_count} ({sum(1 for e in errors if e <= 50)/player_count:.1%})")
    print(f"  Within 100 pts: {sum(1 for e in errors if e <= 100):>4}/{player_count} ({sum(1 for e in errors if e <= 100)/player_count:.1%})")
    print(f"  Within 200 pts: {sum(1 for e in errors if e <= 200):>4}/{player_count} ({sum(1 for e in errors if e <= 200)/player_count:.1%})")
    print(f"  Over   300 pts: {sum(1 for e in errors if e > 300):>4}/{player_count} ({sum(1 for e in errors if e > 300)/player_count:.1%})")

    # 7. Visualizations
    print("\nGenerating visualizations...")
    sns.set_theme(style="whitegrid")
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Plot 1: Players - Real Skill vs Estimated Rating
    player_real = [p.real_skill for p in players]
    player_est = [p.rating for p in players]
    sns.scatterplot(x=player_real, y=player_est, alpha=0.5, ax=axes[0], color='blue')
    axes[0].plot([800, 2200], [800, 2200], 'r--', lw=2)  # Ideal line
    axes[0].set_title("Players: Real Skill vs Estimated Rating")
    axes[0].set_xlabel("Real Skill (Hidden)")
    axes[0].set_ylabel("Estimated Elo Rating")
    
    # Plot 2: Challenges - Real Difficulty vs Estimated Rating
    chal_real = [c.real_difficulty for c in challenges]
    chal_est = [c.rating for c in challenges]
    sns.scatterplot(x=chal_real, y=chal_est, alpha=0.5, ax=axes[1], color='green')
    axes[1].plot([800, 2200], [800, 2200], 'r--', lw=2)  # Ideal line
    axes[1].set_title("Challenges: Real Difficulty vs Estimated Rating")
    axes[1].set_xlabel("Real Difficulty (Hidden)")
    axes[1].set_ylabel("Estimated Elo Rating")
    
    # Plot 3: Rating Error Distribution (Estimated Rating - Real Skill)
    player_errors = [p.rating - p.real_skill for p in players]
    sns.histplot(player_errors, kde=True, ax=axes[2], color='purple', bins=30)
    axes[2].axvline(0, color='r', linestyle='--', lw=2)
    axes[2].set_title("Rating Error Distribution (Players)")
    axes[2].set_xlabel("Error (Estimated - Real)")
    axes[2].set_ylabel("Frequency")
    
    plt.tight_layout()
    plt.show()
