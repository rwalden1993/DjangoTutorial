from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from tictactoe.settings import BOARD_SIZE

GAME_STATUS_CHOICES = (
    ('F', 'First Player to Move'),
    ('S', 'Second Player to Move'),
    ('W', 'First Player Wins'),
    ('L', 'Second Player Wins'),
    ('D', 'Draw')
)


class GamesQuerySet(models.QuerySet):
    def games_for_user(self, user):

        return self.filter(
            Q(first_player=user) | Q(second_player=user)
        )

    def active(self):
        return self.filter(
            Q(status='F') | Q(status='S')
        )


class Game(models.Model):
    first_player = models.ForeignKey(User,
                                     related_name="games_first_player",
                                     on_delete=models.CASCADE)
    second_player = models.ForeignKey(User,
                                      related_name="games_second_player",
                                      on_delete=models.CASCADE)

    start_time = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=1, default='F',
                              choices=GAME_STATUS_CHOICES)

    objects = GamesQuerySet.as_manager()

    def board(self):
        """
        Returns a 2D list of Move objects
        :return:
        """
        board = [[None for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        for move in self.move_set.all():
            board[move.y][move.x] = move
        return board

    def is_user_move(self, user):
        return (user == self.first_player and self.status == 'F') or\
               (user == self.second_player and self.status == 'S')

    def new_move(self):
        """
        Return a new move object with player, game and count present
        :return:
        """
        if self.status not in 'FS':
            raise ValueError("Cannot make a move on a finished game")

        return Move(
            game=self,
            by_first_player=self.status == 'F'
        )

    def update_after_move(self, move):
        """
        Upadate the status of the game, given the last move
        :param move:
        :return:
        """
        self.status = self._get_game_status_after_move(move)

    def get_absolute_url(self):
        return reverse('gameplay_detail', args=[self.id])

    def __str__(self):
        return f'{self.first_player} vs {self.second_player}'

    def _get_game_status_after_move(self, move):
        x, y = move.x, move.y
        board = self.board()
        # look for win
        if (board[y][0] == board[y][1] == board[y][2]) or\
           (board[0][x] == board[1][x] == board[2][x]) or\
           (board[0][0] == board[1][1] == board[2][2]) or\
           (board[0][2] == board[1][1] == board[2][0]):
            return 'W' if move.by_first_player else 'L'
        # look for draw
        if self.move_set.count() >= BOARD_SIZE**2:
            return 'D'
        # other player's move
        return 'S' if self.status == 'F' else 'F'


class Move(models.Model):
    x = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(BOARD_SIZE - 1)]
    )
    y = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(BOARD_SIZE - 1)]
    )
    comment = models.CharField(max_length=300, blank=True)
    game = models.ForeignKey(Game, editable=False, on_delete=models.CASCADE)
    by_first_player = models.BooleanField(editable=False)

    def __eq__(self, other):
        if other is None:
            return False
        return other.by_first_player == self.by_first_player

    def save(self, *args, **kwargs):
        super(Move, self).save(*args, **kwargs)
        self.game.update_after_move(self)
        self.game.save()
