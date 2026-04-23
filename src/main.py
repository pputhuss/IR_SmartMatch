import json
from matcher import rank_companies

def load_companies(path):
    with open(path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    companies = load_companies("../data/companies.json")

    resume_text = """
    Computer Engineering student with hands-on experience in embedded systems
    and firmware development using C and C++. Built microcontroller projects
    using STM32 and Arduino, implemented real-time sensor data processing,
    and developed motor control logic. Coursework includes digital logic,
    computer architecture, and IoT systems.
    """

    ranked = rank_companies(resume_text, companies)

    print("\nTop IR Company Matches:\n")
    print(f"{'Company':<20} {'Score':<10} {'Match Bar'}")
    print("-" * 50)
    for name, score in ranked:
        bar = "|" * int(score * 20)
        print(f"{name:<20} {score:.4f}     {bar}")