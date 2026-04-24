import random
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
            initial_rating=1200,
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

if __name__ == "__main__":
    # 1. Instantiate the Engine
    engine = EloEngine(k_constant=32)

    # 2. Scaling up: Generate large batches of players and challenges
    player_count = 1000
    challenge_count = 500
    
    players = generate_players(player_count)
    challenges = generate_challenges(challenge_count)

    print(f"Arena initialized with {len(players)} players and {len(challenges)} challenges.")

    # 3. Optimized Simulation Loop
    iterations_per_player = 300
    print(f"Starting batch processing ({len(players) * iterations_per_player} total interactions)...")

    for player in players:
        # Each player attempts a unique random sample of challenges
        selected_challenges = random.sample(challenges, iterations_per_player)
        
        for challenge in selected_challenges:
            # Simulate the outcome based on real skills
            result = simulate_attempt(engine, player, challenge)
            
            # Update visible ratings based on the result
            engine.process_result(player, challenge, result)
            
            # Record the new rating for history
            player.record_rating()

    print("Large-scale simulation completed!")

    # 4. Optional: Print a few results to verify
    print("\n--- Sample Results ---")
    for p in random.sample(players, 5):
        print(p)
    
    print("\n--- Sample Challenge Calibration ---")
    for c in random.sample(challenges, 5):
        print(c)
