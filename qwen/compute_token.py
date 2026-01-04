text = """
Established in 1967, the Department of Statistics and Actuarial Science, the University of Hong Kong plays a cross-faculty role inherent in the interdisciplinary nature of the subjects. Through the interrelated functions of teaching, research and consultancy, the Department serves the disciplines of Statistics and Actuarial Science as one of the three divisions under the School of Computing and Data Science. See our Golden Jubilee Celebration.

In the eyes of the Hong Kong community, the Department is best known for its impressive records of admission to various undergraduate and postgraduate degree programmes. Underpinning this enduring dedication to the state-of-the-art teaching is the Department’s profile of world-class research, for it is well known for being a forerunner in many aspects of research and developments and the comprehensiveness of expertise in a diverse range of subjects.

As an international Centre of Actuarial Excellence with a QS World University Ranking of No.24 for the subject of Statistics and Operational Research (in 2025), the Department works to advance Statistics and Actuarial Science both within academia and in society at large.
"""

from dashscope import get_tokenizer

def test(s):
    tokenizer = get_tokenizer('qwen3-plus')
    tokens = tokenizer.encode(s)
    print(f"Token: {len(tokens)}")
    
if __name__ == "__main__":
    test(text)
    
# Token: 227