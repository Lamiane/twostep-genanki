# Set of functions from NLTK library so that I don't need to install it.

def jaro_similarity(s1, s2):
    """
    Computes the Jaro similarity between 2 sequences from:

        Matthew A. Jaro (1989). Advances in record linkage methodology
        as applied to the 1985 census of Tampa Florida. Journal of the
        American Statistical Association. 84 (406): 414-20.

    The Jaro distance between is the min no. of single-character transpositions
    required to change one word into another. The Jaro similarity formula from
    https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance :

        ``jaro_sim = 0 if m = 0 else 1/3 * (m/|s_1| + m/s_2 + (m-t)/m)``

    where
        - `|s_i|` is the length of string `s_i`
        - `m` is the no. of matching characters
        - `t` is the half no. of possible transpositions.
    """
    # First, store the length of the strings
    # because they will be re-used several times.
    len_s1, len_s2 = len(s1), len(s2)

    # The upper bound of the distance for being a matched character.
    match_bound = max(len_s1, len_s2) // 2 - 1

    # Initialize the counts for matches and transpositions.
    matches = 0  # no.of matched characters in s1 and s2
    transpositions = 0  # no. of transpositions between s1 and s2
    flagged_1 = []  # positions in s1 which are matches to some character in s2
    flagged_2 = []  # positions in s2 which are matches to some character in s1

    # Iterate through sequences, check for matches and compute transpositions.
    for i in range(len_s1):  # Iterate through each character.
        upperbound = min(i + match_bound, len_s2 - 1)
        lowerbound = max(0, i - match_bound)
        for j in range(lowerbound, upperbound + 1):
            if s1[i] == s2[j] and j not in flagged_2:
                matches += 1
                flagged_1.append(i)
                flagged_2.append(j)
                break
    flagged_2.sort()
    for i, j in zip(flagged_1, flagged_2):
        if s1[i] != s2[j]:
            transpositions += 1

    if matches == 0:
        return 0
    else:
        return (
            1
            / 3
            * (
                matches / len_s1
                + matches / len_s2
                + (matches - transpositions // 2) / matches
            )
        )



def jaro_winkler_similarity(s1, s2, p=0.1, max_l=4):
    """
    The Jaro Winkler distance is an extension of the Jaro similarity in:

        William E. Winkler. 1990. String Comparator Metrics and Enhanced
        Decision Rules in the Fellegi-Sunter Model of Record Linkage.
        Proceedings of the Section on Survey Research Methods.
        American Statistical Association: 354-359.

    such that:

        jaro_winkler_sim = jaro_sim + ( l * p * (1 - jaro_sim) )

    where,

    - jaro_sim is the output from the Jaro Similarity,
        see jaro_similarity()
    - l is the length of common prefix at the start of the string
        - this implementation provides an upperbound for the l value
            to keep the prefixes.A common value of this upperbound is 4.
    - p is the constant scaling factor to overweigh common prefixes.
        The Jaro-Winkler similarity will fall within the [0, 1] bound,
        given that max(p)<=0.25 , default is p=0.1 in Winkler (1990)


    Test using outputs from https://www.census.gov/srd/papers/pdf/rr93-8.pdf
    from "Table 5 Comparison of String Comparators Rescaled between 0 and 1"

    >>> winkler_examples = [("billy", "billy"), ("billy", "bill"), ("billy", "blily"),
    ... ("massie", "massey"), ("yvette", "yevett"), ("billy", "bolly"), ("dwayne", "duane"),
    ... ("dixon", "dickson"), ("billy", "susan")]

    >>> winkler_scores = [1.000, 0.967, 0.947, 0.944, 0.911, 0.893, 0.858, 0.853, 0.000]
    >>> jaro_scores =    [1.000, 0.933, 0.933, 0.889, 0.889, 0.867, 0.822, 0.790, 0.000]

    One way to match the values on the Winkler's paper is to provide a different
    p scaling factor for different pairs of strings, e.g.

    >>> p_factors = [0.1, 0.125, 0.20, 0.125, 0.20, 0.20, 0.20, 0.15, 0.1]

    >>> for (s1, s2), jscore, wscore, p in zip(winkler_examples, jaro_scores, winkler_scores, p_factors):
    ...     assert round(jaro_similarity(s1, s2), 3) == jscore
    ...     assert round(jaro_winkler_similarity(s1, s2, p=p), 3) == wscore


    Test using outputs from https://www.census.gov/srd/papers/pdf/rr94-5.pdf from
    "Table 2.1. Comparison of String Comparators Using Last Names, First Names, and Street Names"

    >>> winkler_examples = [('SHACKLEFORD', 'SHACKELFORD'), ('DUNNINGHAM', 'CUNNIGHAM'),
    ... ('NICHLESON', 'NICHULSON'), ('JONES', 'JOHNSON'), ('MASSEY', 'MASSIE'),
    ... ('ABROMS', 'ABRAMS'), ('HARDIN', 'MARTINEZ'), ('ITMAN', 'SMITH'),
    ... ('JERALDINE', 'GERALDINE'), ('MARHTA', 'MARTHA'), ('MICHELLE', 'MICHAEL'),
    ... ('JULIES', 'JULIUS'), ('TANYA', 'TONYA'), ('DWAYNE', 'DUANE'), ('SEAN', 'SUSAN'),
    ... ('JON', 'JOHN'), ('JON', 'JAN'), ('BROOKHAVEN', 'BRROKHAVEN'),
    ... ('BROOK HALLOW', 'BROOK HLLW'), ('DECATUR', 'DECATIR'), ('FITZRUREITER', 'FITZENREITER'),
    ... ('HIGBEE', 'HIGHEE'), ('HIGBEE', 'HIGVEE'), ('LACURA', 'LOCURA'), ('IOWA', 'IONA'), ('1ST', 'IST')]

    >>> jaro_scores =   [0.970, 0.896, 0.926, 0.790, 0.889, 0.889, 0.722, 0.467, 0.926,
    ... 0.944, 0.869, 0.889, 0.867, 0.822, 0.783, 0.917, 0.000, 0.933, 0.944, 0.905,
    ... 0.856, 0.889, 0.889, 0.889, 0.833, 0.000]

    >>> winkler_scores = [0.982, 0.896, 0.956, 0.832, 0.944, 0.922, 0.722, 0.467, 0.926,
    ... 0.961, 0.921, 0.933, 0.880, 0.858, 0.805, 0.933, 0.000, 0.947, 0.967, 0.943,
    ... 0.913, 0.922, 0.922, 0.900, 0.867, 0.000]

    One way to match the values on the Winkler's paper is to provide a different
    p scaling factor for different pairs of strings, e.g.

    >>> p_factors = [0.1, 0.1, 0.1, 0.1, 0.125, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.20,
    ... 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]


    >>> for (s1, s2), jscore, wscore, p in zip(winkler_examples, jaro_scores, winkler_scores, p_factors):
    ...     if (s1, s2) in [('JON', 'JAN'), ('1ST', 'IST')]:
    ...         continue  # Skip bad examples from the paper.
    ...     assert round(jaro_similarity(s1, s2), 3) == jscore
    ...     assert round(jaro_winkler_similarity(s1, s2, p=p), 3) == wscore



    This test-case proves that the output of Jaro-Winkler similarity depends on
    the product  l * p and not on the product max_l * p. Here the product max_l * p > 1
    however the product l * p <= 1

    >>> round(jaro_winkler_similarity('TANYA', 'TONYA', p=0.1, max_l=100), 3)
    0.88
    """
    # To ensure that the output of the Jaro-Winkler's similarity
    # falls between [0,1], the product of l * p needs to be
    # also fall between [0,1].
    if not 0 <= max_l * p <= 1:
        warnings.warn(
            str(
                "The product  `max_l * p` might not fall between [0,1]."
                "Jaro-Winkler similarity might not be between 0 and 1."
            )
        )

    # Compute the Jaro similarity
    jaro_sim = jaro_similarity(s1, s2)

    # Initialize the upper bound for the no. of prefixes.
    # if user did not pre-define the upperbound,
    # use shorter length between s1 and s2

    # Compute the prefix matches.
    l = 0
    # zip() will automatically loop until the end of shorter string.
    for s1_i, s2_i in zip(s1, s2):
        if s1_i == s2_i:
            l += 1
        else:
            break
        if l == max_l:
            break
    # Return the similarity value as described in docstring.
    return jaro_sim + (l * p * (1 - jaro_sim))