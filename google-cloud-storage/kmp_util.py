def computeLPSArray(pattern):
    """
    Computes the Longest Prefix Suffix (LPS) array for a given pattern.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of the previous longest prefix suffix
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmpSearch(text, pattern):
    """
    Searches for the pattern in the text using the KMP algorithm.
    Prints all occurrences of the pattern.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        print("Pattern cannot be empty")
        return

    lps = computeLPSArray(pattern)

    i = 0  # index for text[]
    j = 0  # index for pattern[]
    found_indices = []

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            found_indices.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return found_indices