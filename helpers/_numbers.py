from random import randint


class Numbers(object):
    """
    Numbers class has most frequent operations on Numbers.
    """
    @staticmethod
    def generate_random_number(length):
        """
        generates random number with desired length
        """
        range_start = 10**(length-1)
        range_end = (10**length)-1
        return randint(range_start, range_end)
