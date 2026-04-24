import math
from models.player import Player
from models.challenge import Challenge

class EloEngine:
    def __init__(self):
        pass

    def calculate_expectation(self, rating_a: float, rating_b: float) -> float:
        """Calculates the probability (0.0 to 1.0) of A beating B."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def get_dynamic_k(self, attempts: int) -> int:
        """
        Calculates a dynamic K-factor based on the number of interactions.
        Fast calibration for new entries, stable for established ones.
        """
        if attempts < 20:
            return 64  # Placement matches
        elif attempts < 60:
            return 32  # Standard adjustment
        else:
            return 16  # Established rank

    def process_result(self, player: Player, challenge: Challenge, win: int):
        """
        Updates the ratings and statistics for both instances.
        win: 1 if the student got it right, 0 if they got it wrong.
        """
        # 1. Calculate the expected probability of success
        exp_player = self.calculate_expectation(player.rating, challenge.rating)
        exp_challenge = 1 - exp_player 

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
        if win == 1:
            challenge.success_count += 1
        else:
            challenge.failure_count += 1

        # 5. Update Ratings (Elo Math)
        player.rating = player.rating + k_player * (win - exp_player)
        
        challenge_result = 1 - win 
        challenge.rating = challenge.rating + k_challenge * (challenge_result - exp_challenge)
