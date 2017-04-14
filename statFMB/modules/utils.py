
#checks for a typo between 2 strings
#if s1 == s2 returns False(it's not a typo but the same word)
def is_typo(s1, s2):
    count_diffs = 0
    if len(s1) == len(s2):
        for a, b in zip(s1,s2):
            if a != b:
                if count_diffs :return False
                count_diffs += 1
        else:
            return True
    else:
        return False

