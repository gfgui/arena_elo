class Player:
    def __init__(self, player_id: int, name: str, initial_rating: float = 1200.0, real_skill: float = 1200.0):
        self.player_id = player_id
        self.name = name
        self.rating = initial_rating
        self.real_skill = real_skill
        
        # Statistics
        self.total_attempts = 0
        self.success_count = 0
        self.sum_challenge_ratings = 0.0
        
        # History
        self.rating_history = [initial_rating]

    @property
    def accuracy(self) -> float:
        return self.success_count / self.total_attempts if self.total_attempts > 0 else 0.0

    @property
    def average_difficulty_faced(self) -> float:
        return self.sum_challenge_ratings / self.total_attempts if self.total_attempts > 0 else 0.0

    def record_rating(self):
        self.rating_history.append(self.rating)

    def __str__(self):
        return (f"[{self.player_id}] {self.name} | Elo: {self.rating:.0f} (Real: {self.real_skill}) | "
                f"Acc: {self.accuracy:.1%} | Avg Diff: {self.average_difficulty_faced:.0f}")

    def __repr__(self):
        return self.__str__()
