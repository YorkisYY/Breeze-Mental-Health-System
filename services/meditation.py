import pandas as pd

def load_resources_from_file(file_path="resources.csv"):
    """加载 CSV 文件并返回 DataFrame"""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None


def search_resources_from_file(df, keyword):
    """根据关键字在 DataFrame 中搜索资源"""
    matches = df[df["Keyword"].str.contains(keyword, case=False)]
    if not matches.empty:
        return matches
    else:
        return None


# 定义类别和子选项
CATEGORIES = {
    "1": {
        "name": "Sleep Health",
        "options": {
            "1": "Getting to Sleep",
            "2": "Staying Asleep",
            "3": "Sleep Quality"
        }
    },
    "2": {
        "name": "Mental Health",
        "options": {
            "1": "Stress & Burnout",
            "2": "Anxiety",
            "3": "Fear",
            "4": "Sadness & Loneliness",
            "5": "Self-Confidence",
            "6": "Relationships & Breakups",
            "7": "Pregnancy & Parenting"
        }
    },
    "3": {
        "name": "Peak Productivity",
        "options": {
            "1": "Happiness & Joy",
            "2": "Gratitude & Abundance",
            "3": "Performance & Productivity",
            "4": "Focus & Deep Work",
            "5": "Grit & Resilience"
        }
    },
    "4": {
        "name": "Spiritual Health",
        "options": {
            "1": "Meditation & Mindfulness",
            "2": "Music & Sound Meditation",
            "3": "Chanting & Mantras",
            "4": "Manifesting & Affirmations",
            "5": "Breathwork",
            "6": "Morning Routines",
            "7": "Yoga",
            "8": "Buddhism",
            "9": "Spiritual Paths",
            "10": "Religious Paths"
        }
    }
}

def handle_search_meditation():
    """处理搜索冥想资源的逻辑"""
    file_path = "resources.csv"
    df = load_resources_from_file(file_path)

    if df is None:
        print("Error: Could not load meditation resources.")
        return

    while True:
        print("\nSearch Meditation Resources:")
        print("1. I want to explore based on my needs")
        print("2. I want to search by keyword")
        print("3. Return to the main menu")
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            handle_needs_based_search(df)
        elif choice == "2":
            handle_keyword_search(df)
        elif choice == "3":
            print("Returning to the main menu.")
            break
        else:
            print("Invalid choice, please try again.")

def handle_needs_based_search(df):
    """通过需求问答找到资源"""
    print("\nWhat do you need?")
    for category_key, category in CATEGORIES.items():
        print(f"{category_key}. {category['name']}")
    category_choice = input("Select a category (1-4): ").strip()

    if category_choice in CATEGORIES:
        category = CATEGORIES[category_choice]
        print(f"\n{category['name']} Options:")
        for option_key, option in category["options"].items():
            print(f"{option_key}. {option}")
        sub_option = input("Select an option: ").strip()

        if sub_option in category["options"]:
            selected_option = category["options"][sub_option]
            # 在资源中查找匹配的链接
            matches = df[df["Title"].str.contains(selected_option, case=False)]
            if not matches.empty:
                print("\nHere are your resources:")
                for _, row in matches.iterrows():
                    print(f"- {row['Title']}: {row['URL']}")
            else:
                print(f"No resources found for '{selected_option}'.")
        else:
            print("Invalid option.")
    else:
        print("Invalid category.")

def handle_keyword_search(df):
    """直接通过关键字搜索资源"""
    while True:
        keyword = input("\nEnter a keyword to search for resources (or type 'exit' to return): ").strip().lower()
        if keyword == "exit":
            print("Returning to the previous menu.")
            break

        result = search_resources_from_file(df, keyword)
        if result is not None and not result.empty:
            print("\nFound the following resources:")
            for _, row in result.iterrows():
                print(f"- {row['Title']}: {row['URL']}")
        else:
            print(f"No resources found for '{keyword}'. Try another keyword.")