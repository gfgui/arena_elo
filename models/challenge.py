class Challenge:
    def __init__(self, challenge_id: int, topic: str, initial_rating: float = 1200.0, real_difficulty: float = 1200.0):
        self.challenge_id = challenge_id
        self.topic = topic
        self.rating = initial_rating
        self.real_difficulty = real_difficulty
        
        # Statistics
        self.total_attempts = 0
        self.success_count = 0  # Number of students who solved it
        self.failure_count = 0  # Number of students who failed it
        self.sum_player_ratings = 0.0  # Sum of player ratings who attempted

    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_attempts if self.total_attempts > 0 else 0.0

    def __str__(self):
        return (f"[{self.challenge_id}] {self.topic} | Elo: {self.rating:.0f} (Real: {self.real_difficulty}) | "
                f"Success Rate: {self.success_rate:.1%} | Attempts: {self.total_attempts}")

    def __repr__(self):
        return self.__str__()
