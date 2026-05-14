import math
from models.player import Player
from models.challenge import Challenge

class EloEngine:
    def __init__(self):
        # Store all results for MLE recalibration
        self._results: list[tuple[int, int, int]] = []  # (player_id, challenge_id, win)

    def calculate_expectation(self, rating_a: float, rating_b: float) -> float:
        """Calculates the probability (0.0 to 1.0) of A beating B."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def get_dynamic_k(self, attempts: int) -> float:
        """
        Calculates a dynamic K-factor using logarithmic decay.
        Starts high (64) and decays smoothly, never going below 10.
        """
        if attempts < 1:
            return 64.0
        k_start = 64.0
        k_min = 10.0
        decay_rate = 0.6
        k = k_start / (1 + decay_rate * math.log(1 + attempts))
        return max(k_min, k)

    def process_result(self, player: Player, challenge: Challenge, win: int):
        """
        Updates the ratings and statistics for both instances.
        win: 1 if the student got it right, 0 if they got it wrong.
        """
        # 1. Calculate the expected probability of success
        exp_player = self.calculate_expectation(player.rating, challenge.rating)

        # 2. Get dynamic K for both
        k_player = self.get_dynamic_k(player.total_attempts)
        k_challenge = self.get_dynamic_k(challenge.total_attempts)

        # 3. Update Player Statistics
        player.total_attempts += 1
        player.sum_challenge_ratings += challenge.rating
        if win == 1:
            player.success_count += 1

        # 4. Update Challenge Statistics
        challenge.total_attempts += 1
        challenge.sum_player_ratings += player.rating
        if win == 1:
            challenge.success_count += 1
        else:
            challenge.failure_count += 1

        # 5. Standard Elo update
        player.rating += k_player * (win - exp_player)
        
        challenge_result = 1 - win
        exp_challenge = 1 - exp_player
        challenge.rating += k_challenge * (challenge_result - exp_challenge)
        
        # 6. Store result for batch recalibration
        self._results.append((player.player_id, challenge.challenge_id, win))

    def recalibrate_mle(self, players: list[Player], challenges: list[Challenge], 
                        anchor_challenges: dict[int, float] = None,
                        iterations: int = 100):
        """
        Maximum Likelihood Estimation (MLE) recalibration with anchoring.
        
        The Elo expectation formula E = 1/(1+10^((Rb-Ra)/400)) only depends
        on the DIFFERENCE (Rb - Ra). This means adding a constant to ALL 
        ratings produces the same likelihood — the system is translation-invariant.
        
        To break this degeneracy, we need ANCHORS: entities with known ratings.
        In practice, you'd have a set of calibrated "benchmark" challenges.
        In simulation, we anchor a sample of challenges to their real difficulty.
        
        anchor_challenges: dict of {challenge_id: known_real_difficulty}
        """
        player_map = {p.player_id: p for p in players}
        challenge_map = {c.challenge_id: c for c in challenges}
        
        # Group results
        player_results: dict[int, list[tuple[int, int]]] = {}
        challenge_results: dict[int, list[tuple[int, int]]] = {}
        
        for pid, cid, win in self._results:
            player_results.setdefault(pid, []).append((cid, win))
            challenge_results.setdefault(cid, []).append((pid, win))
        
        scale = math.log(10) / 400.0
        lr = 40.0
        
        if anchor_challenges is None:
            anchor_challenges = {}
        
        for iteration in range(iterations):
            total_adjustment = 0.0
            
            # Update player ratings
            for pid, results in player_results.items():
                player = player_map[pid]
                gradient = 0.0
                for cid, win in results:
                    challenge = challenge_map[cid]
                    expected = self.calculate_expectation(player.rating, challenge.rating)
                    gradient += (win - expected)
                gradient *= scale
                
                adjustment = lr * gradient
                adjustment = max(-100, min(100, adjustment))
                player.rating += adjustment
                total_adjustment += abs(adjustment)
            
            # Update challenge ratings (with anchoring)
            for cid, results in challenge_results.items():
                challenge = challenge_map[cid]
                gradient = 0.0
                for pid, win in results:
                    player = player_map[pid]
                    expected = self.calculate_expectation(challenge.rating, player.rating)
                    challenge_win = 1 - win
                    gradient += (challenge_win - expected)
                gradient *= scale
                
                # Strong anchor regularization for known challenges
                if cid in anchor_challenges:
                    anchor_value = anchor_challenges[cid]
                    n_results = len(results)
                    # Force anchor convergence by using a much stronger gradient
                    # This acts as a 'virtual' set of many games against fixed values
                    anchor_grad = -scale * (challenge.rating - anchor_value)
                    gradient += anchor_grad * (n_results + 20)
                
                adjustment = lr * gradient
                adjustment = max(-100, min(100, adjustment))
                challenge.rating += adjustment
                total_adjustment += abs(adjustment)
            
            avg_adj = total_adjustment / (len(players) + len(challenges))
            if avg_adj < 0.01:
                print(f"    MLE converged at iteration {iteration + 1} (avg adjustment: {avg_adj:.4f})")
                break
        else:
            print(f"    MLE completed {iterations} iterations (avg adjustment: {avg_adj:.3f})")
