import math
from models.player import Player
from models.challenge import Challenge

class EloEngine:
    def __init__(self, k_constant: int = 32):
        self.k_constant = k_constant

    def calculate_expectation(self, rating_a: float, rating_b: float) -> float:
        """Calculates the probability (0.0 to 1.0) of A beating B."""
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def process_result(self, player: Player, challenge: Challenge, win: int):
        """
        Updates the ratings and statistics for both instances.
        win: 1 if the student got it right, 0 if they got it wrong.
        """
        # 1. Calculate the expected probability of success based on current VISIBLE ratings
        exp_player = self.calculate_expectation(player.rating, challenge.rating)
        exp_challenge = 1 - exp_player 

        # 2. Update Player Statistics
        player.total_attempts += 1
        player.sum_challenge_ratings += challenge.rating
        if win == 1:
            player.success_count += 1

        # 3. Update Challenge Statistics
        challenge.total_attempts += 1
        if win == 1:
            challenge.success_count += 1
        else:
            challenge.failure_count += 1

        # 4. Update Ratings (Elo Math)
        player.rating = player.rating + self.k_constant * (win - exp_player)
        
        challenge_result = 1 - win 
        challenge.rating = challenge.rating + self.k_constant * (challenge_result - exp_challenge)
