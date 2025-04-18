from flask import render_template, request, redirect, url_for, session
from app import app
import json
import os
import random

# 詩データの読み込み
data_path = os.path.join(os.path.dirname(__file__), '../data/data.json')
with open(data_path, encoding='utf-8') as f:
    poetry_data = json.load(f)

# セッションで選択肢保存を有効化
app.secret_key = 'your_secret_key_here'

@app.route('/')
def index():
    step1 = poetry_data['step1']
    return render_template('index.html', step1=step1)

@app.route('/step2', methods=['POST'])
def step2():
    session['step1_choice'] = request.form
    step2 = poetry_data['step2']
    return render_template('step2.html', step2=step2)

@app.route('/step3', methods=['POST'])
def step3():
    session['step2_choice'] = request.form
    step3 = poetry_data['step3']
    return render_template('step3.html', step3=step3)

@app.route('/result', methods=['POST'])
def result():
    session['step3_choice'] = request.form

    # 全ステップの選択肢を集めてスコア集計
    total_score = {}
    for step_key in ['step1_choice', 'step2_choice', 'step3_choice']:
        for theme, choice in session.get(step_key, {}).items():
            step_name = step_key.replace('_choice', '')
            if step_name in poetry_data and theme in poetry_data[step_name]:
                choice_data = next(
                    (item for item in poetry_data[step_name][theme] if item['text'] == choice),
                    None
                )
                if choice_data:
                    attr = choice_data['attribute']
                    strength = int(choice_data['strength'])
                    total_score[attr] = total_score.get(attr, 0) + strength

    # スコアが空だったときの処理
    if not total_score:
        ending_type = '中立'
    else:
        ending_type = max(total_score, key=total_score.get)

    # エンディングの取得（なければランダムで必ず一つ表示）
    endings = poetry_data.get('endings', {})
    possible_endings = endings.get(ending_type, [])
    if possible_endings:
        result_line = random.choice(possible_endings)['text']
    else:
        # すべてのエンディングからランダムに一つ選ぶ
        all_endings = [e['text'] for end_list in endings.values() for e in end_list if 'text' in e]
        result_line = random.choice(all_endings) if all_endings else '……まだ言葉にならない想いが、そこにある。'

    # エンディング属性に応じた背景色
    background_colors = {
    '希望': '#ffe9ec',      # やさしいピンク
    '絶望': '#0f0f23',      # 深い藍色
    '中立': '#e8e8e8',      # 霧のようなグレー
    '境界': '#d8cfff',      # 淡い紫
    '自己肯定': '#f6f5e8',  # 柔らかいアイボリー
    '受容': '#fcf4de',      # 淡いオレンジベージュ
    '無力': '#b6b6b6',      # くすんだグレー
    '恐れ': '#3a1f5d',      # 暗い紫
    '冷静': '#d0f0ff',      # 氷のような青
    '解放': '#fffbe7'       # 透けるような白黄色
}

    bg_color = background_colors.get(ending_type, '#ffffff')

    return render_template(
        'result.html',
        step1=session.get('step1_choice', {}),
        step2=session.get('step2_choice', {}),
        step3=session.get('step3_choice', {}),
        result=result_line,
        background_color=bg_color
    )