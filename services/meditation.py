import pandas as pd



def load_resources_from_file(file_path="data/meditation_resources.csv"):
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

def levenshtein_distance(s1, s2):
    """计算两个字符串的 Levenshtein 距离"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1, s2):
    """计算两个字符串的相似度"""
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    return 1 - levenshtein_distance(s1, s2) / max_len


def custom_fuzzy_search(keyword, keywords_list, threshold=0.6):
    """模糊搜索，匹配多个关键字中的任意一个"""
    matches = []
    for keywords in keywords_list:
        for k in keywords:
            if similarity_ratio(keyword, k) >= threshold:
                matches.append(keywords)
                break
    return matches

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

def load_resources_from_file(file_path="data/meditation_resources.csv"):
    """加载 CSV 文件并返回 DataFrame"""
    try:
        print(f"Attempting to load file: {file_path}")  # 添加调试信息
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")  # 文件不存在
        return None
    except Exception as e:
        print(f"Error loading file: {e}")  # 其他未知错误
        return None


def handle_search_meditation():
    """处理搜索冥想资源的逻辑"""
    file_path = "data/meditation_resources.csv"
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
            selected_option = selected_option.strip().lower()  # 标准化用户输入

            # 修正为匹配 Subtitle 列
            df["Subtitle"] = df["Subtitle"].str.strip().str.lower()  # 标准化数据
            matches = df[df["Subtitle"].str.contains(selected_option, case=False)]
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
    """直接通过关键字搜索资源，支持模糊匹配"""
    # 标准化数据并展开关键词
    df["Keyword"] = df["Keyword"].str.split(",").apply(lambda x: [k.strip().lower() for k in x])
    df["Subtitle"] = df["Subtitle"].str.strip().str.lower()
    df_exploded = df.explode('Keyword').reset_index(drop=True)
    df_exploded["Keyword"] = df_exploded["Keyword"].str.strip().str.lower()

    while True:
        keyword = input("\nEnter a keyword to search for resources (or type 'exit' to return): ").strip().lower()
        if keyword == "exit":
            print("Returning to the previous menu.")
            break

        # 精确匹配
        exact_matches = df_exploded[(df_exploded["Keyword"] == keyword) | (df_exploded["Subtitle"] == keyword)]
        if not exact_matches.empty:
            print("\nExact match found:")
            for _, row in exact_matches.iterrows():
                print(f"- {row['Title']} - {row['Subtitle']}: {row['URL']}")
            continue

        # 模糊匹配
        df_exploded["Keyword_Similarity"] = df_exploded["Keyword"].apply(lambda k: similarity_ratio(keyword, k))
        df_exploded["Subtitle_Similarity"] = df_exploded["Subtitle"].apply(lambda s: similarity_ratio(keyword, s))
        fuzzy_matches = df_exploded[(df_exploded["Keyword_Similarity"] >= 0.6) | (df_exploded["Subtitle_Similarity"] >= 0.6)]
        if not fuzzy_matches.empty:
            print("\nHere are the closest matches:")
            # 去重，避免重复显示相同的资源
            fuzzy_matches = fuzzy_matches.drop_duplicates(subset=['Title', 'Subtitle', 'URL'])
            for _, row in fuzzy_matches.iterrows():
                print(f"- {row['Title']} - {row['Subtitle']}: {row['URL']}")
        else:
            print(f"No resources found for '{keyword}'. Try another keyword.")
