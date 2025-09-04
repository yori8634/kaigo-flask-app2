
from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def judge_kaigo_applicability(row):
    valid_levels = ['要支援1', '要支援2', '要介護1', '要介護2', '要介護3', '要介護4', '要介護5']
    if row['kaigo_level'] not in valid_levels:
        return False, "介護認定が未取得"
    if row['work_type'] == "手すり設置" and row['location'] in ["廊下", "トイレ", "浴室", "玄関"] and "固定" in row['detail']:
        return True, "固定式手すりは対象"
    elif row['work_type'] == "段差解消" and "段差" in row['detail']:
        try:
            height = int(row['detail'].replace("段差", "").replace("cm", "").strip())
            if height >= 3:
                return True, f"{height}cmの段差解消は対象"
        except:
            return False, "段差高さ不明"
    elif row['work_type'] == "床材変更" and "滑り" in row['detail']:
        return True, "滑り防止床材は対象"
    elif row['work_type'] == "扉交換" and "引き戸" in row['detail']:
        return True, "引き戸への交換は対象"
    elif row['work_type'] == "洋式便器交換" and "和式" in row['detail']:
        return True, "和式→洋式は対象"
    elif row['work_type'] == "付帯工事":
        return True, "付帯工事は対象"
    else:
        return False, "対象外の改修内容"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)
        df[['is_applicable', 'reason']] = df.apply(judge_kaigo_applicability, axis=1, result_type='expand')

        # HTML表示用にテーブル変換
        table_html = df.to_html(classes='table table-bordered', index=False, justify='center')
        return render_template('index.html', table=table_html)

    return render_template('index.html', table=None)

# ✅ Render対応の起動設定
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
