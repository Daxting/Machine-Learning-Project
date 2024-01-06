import joblib
model_simple_pretrained = joblib.load('diabetes_model_simple.pkl')
#['HighBP', 'HighChol', 'BMI', 'GenHlth', 'DiffWalk']
model_complex_pretrained = joblib.load('diabetes_model_complex.pkl')
#['HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies', 'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education']

import numpy as np
import pandas as pd
import csv
import os
 
from flask import Flask, request, render_template
app = Flask(__name__, template_folder='templates')
 
 
def write_form_data_to_csv(form_data, csv_filename='form_data.csv'):
    # 取得當前執行檔案的資料夾路徑
    current_directory = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_directory, csv_filename)

    # 如果檔案不存在，則建立新檔案
    if not os.path.isfile(csv_path):
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = form_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # 如果表單類型是 'preliminary'，排除 'MentHlth', 'PhysHlth', 'Age', 'Education'，其餘寫入表單資料
    if form_data.get('assessment_type_hidden') == 'preliminary':
        with open(csv_path, 'a', newline='') as csvfile:
            # 複製一份 form_data，刪除 'MentHlth', 'PhysHlth', 'Age', 'Education'
            data_to_write = form_data.copy()
            for key in ['MentHlth', 'PhysHlth', 'Age', 'Education']:
                if key in data_to_write:
                    del data_to_write[key]

            # 設定寫入的欄位
            fieldnames = [key for key in data_to_write.keys()]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 如果檔案是空的，寫入表頭
            if csvfile.tell() == 0:
                writer.writeheader()

            # 寫入表單資料
            writer.writerow(data_to_write)
            print(f"表單資料 {data_to_write} 已儲存至 {csv_filename}")
    else:
        # 如果表單類型不是 'preliminary'，則全部寫入
        with open(csv_path, 'a', newline='') as csvfile:
            fieldnames = form_data.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 如果檔案是空的，寫入表頭
            if csvfile.tell() == 0:
                writer.writeheader()

            # 寫入表單資料
            writer.writerow(form_data)
            print(f"表單資料 {form_data} 已儲存至 {csv_filename}")

    return


def process_data(file_path='form_data.csv'):
    # 讀取CSV檔案，將指定的空值視為NaN
    df = pd.read_csv(file_path, na_values=['', 'NA', 'null', 'None'])
    # 只保留最後一行數據
    df = df.tail(1)
    # 刪除包含缺失值的行
    df = df.dropna(axis=1)  # 這裡使用 axis=1 代表針對列進行操作
    # 刪除欄位
    df = df.drop(columns=['fieldsetOption'])
    df = df.drop(columns=['assessment_type_hidden'])
    # 將 'Height' 和 'Weight' 欄位轉換為數字型態
    df[['Height', 'Weight']] = df[['Height', 'Weight']].apply(pd.to_numeric, errors='coerce')
    # 計算BMI，新增 'BMI' 欄位
    if not df['Height'].isna().any() and not df['Weight'].isna().any():
        df['BMI'] = df['Weight'] / ((df['Height'] / 100) ** 2)
        # 刪除 'Height' 和 'Weight' 欄位
        df = df.drop(columns=['Height', 'Weight'])
    # 返回處理後的資料
    return df
    

@app.route("/")
def formPage():
    title="diabetes evaluation website"
    return render_template('index.html', title=title)


@app.route("/submit", methods=['POST'])
def submit():
    if request.method == 'POST':
        form_data = request.form
        #建立資料庫在同資料夾下的csv
        
        if(form_data['assessment_type_hidden']=='preliminary'):
            type='simple'
        else:
            type='complex'

        write_form_data_to_csv(form_data)
        processed_data=process_data('form_data.csv')
        #####在submit後，保留提交前的結果#####
        print("-----processed_data basic info start-----")
        print(processed_data.info)
        print("-----processed_data basic info end-----")
        if(type=='simple'):
            #['HighBP', 'HighChol', 'BMI', 'GenHlth', 'DiffWalk']
            result = model_simple_pretrained.predict([[int(processed_data['HighBP']), int(processed_data['HighChol'])
                , int(processed_data['DiffWalk']),int(processed_data['GenHlth']),int(processed_data['BMI'])]])
            result_proba = model_simple_pretrained.predict_proba([[int(processed_data['HighBP']), int(processed_data['HighChol'])
                , int(processed_data['DiffWalk']),int(processed_data['GenHlth']),int(processed_data['BMI'])]])
        else:   
            #['HighBP', 'HighChol', 'CholCheck', 'BMI', 'Smoker', 'Stroke', 'HeartDiseaseorAttack', 'PhysActivity', 'Fruits', 'Veggies', 
            #'HvyAlcoholConsump', 'AnyHealthcare', 'NoDocbcCost', 'GenHlth', 'MentHlth', 'PhysHlth', 'DiffWalk', 'Sex', 'Age', 'Education']
            result = model_complex_pretrained.predict([[int(processed_data['HighBP']), int(processed_data['HighChol']), int(form_data['CholCheck'])
                , int(processed_data['BMI']), int(form_data['Smoker']), int(form_data['Stroke']), int(form_data['HeartDiseaseorAttack'])
                , int(form_data['PhysActivity']), int(form_data['Fruits']), int(form_data['Veggies']), int(form_data['HvyAlcoholConsump'])
                , int(form_data['AnyHealthcare']), int(form_data['NoDocbcCost']), int(form_data['GenHlth']), int(form_data['MentHlth'])
                , int(form_data['PhysHlth']), int(form_data['DiffWalk']), int(form_data['Sex']), int(form_data['Age']), int(form_data['Education']), ]])
            result_proba = model_complex_pretrained.predict_proba([[int(processed_data['HighBP']), int(processed_data['HighChol']), int(form_data['CholCheck'])
                , int(processed_data['BMI']), int(form_data['Smoker']), int(form_data['Stroke']), int(form_data['HeartDiseaseorAttack'])
                , int(form_data['PhysActivity']), int(form_data['Fruits']), int(form_data['Veggies']), int(form_data['HvyAlcoholConsump'])
                , int(form_data['AnyHealthcare']), int(form_data['NoDocbcCost']), int(form_data['GenHlth']), int(form_data['MentHlth'])
                , int(form_data['PhysHlth']), int(form_data['DiffWalk']), int(form_data['Sex']), int(form_data['Age']), int(form_data['Education']), ]])
        
        predicted_class = result[0]  # 預測的類別
        class_probabilities = result_proba[0]  # 每個類別的概率
        if predicted_class == 2:
            prediction = f'糖尿病高風險 - 系統信心 {class_probabilities[2]:.10f} %'
        elif predicted_class == 1:
            prediction = f'糖尿病低風險 - 系統信心 {class_probabilities[1]:.10f} %'
        else:
            prediction = f'無糖尿病風險 - 系統信心 {class_probabilities[0]:.10f} %'


        #預選原本使用者勾選的選項
        Height = form_data['Height']
        Weight = form_data['Weight']
        # HighBP
        HighBP_Yes = ''
        HighBP_No = ''
        if int(form_data['HighBP']) == 1:
            HighBP_Yes = 'checked'
        else:
            HighBP_No = 'checked'
        # HighChol
        HighChol_Yes = ''
        HighChol_No = ''
        if int(form_data['HighChol']) == 1:
            HighChol_Yes = 'checked'
        else:
            HighChol_No = 'checked'
        

        # GenHlth
        GenHlth_0 = ''
        GenHlth_1 = ''
        GenHlth_2 = ''
        GenHlth_3 = ''
        GenHlth_4 = ''
        GenHlth_5 = ''
        if int(form_data['GenHlth']) == 0:
            GenHlth_0 = 'selected'
        elif int(form_data['GenHlth']) == 1:
            GenHlth_1 = 'selected'
        elif int(form_data['GenHlth']) == 2:
            GenHlth_2 = 'selected'
        elif int(form_data['GenHlth']) == 3:
            GenHlth_3 = 'selected'
        elif int(form_data['GenHlth']) == 4:
            GenHlth_4 = 'selected'
        else:
            GenHlth_5 = 'selected'
        # DiffWalk
        DiffWalk_Yes = ''
        DiffWalk_No = ''
        if int(form_data['DiffWalk']) == 1:
            DiffWalk_Yes = 'checked'
        else:
            DiffWalk_No = 'checked'

        if type=='simple':
            return render_template('index.html', Height=Height, Weight=Weight, HighBP_Yes=HighBP_Yes, HighBP_No=HighBP_No,
                    HighChol_Yes=HighChol_Yes, HighChol_No=HighChol_No,
                    GenHlth_0=GenHlth_0, GenHlth_1=GenHlth_1, GenHlth_2=GenHlth_2, GenHlth_3=GenHlth_3,
                    GenHlth_4=GenHlth_4, GenHlth_5=GenHlth_5,
                    DiffWalk_Yes=DiffWalk_Yes, DiffWalk_No=DiffWalk_No, prediction=prediction)
        else:
            # CholCheck
            CholCheck_Yes = ''
            CholCheck_No = ''
            if int(form_data['CholCheck']) == 1:
                CholCheck_Yes = 'checked'
            else:
                CholCheck_No = 'checked'
            # Smoker
            Smoker_Yes = ''
            Smoker_No = ''
            if int(form_data['Smoker']) == 1:
                Smoker_Yes = 'checked'
            else:
                Smoker_No = 'checked'
            # Stroke
            Stroke_Yes = ''
            Stroke_No = ''
            if int(form_data['Stroke']) == 1:
                Stroke_Yes = 'checked'
            else:
                Stroke_No = 'checked'
            # HeartDiseaseorAttack
            HeartDiseaseorAttack_Yes = ''
            HeartDiseaseorAttack_No = ''
            if int(form_data['HeartDiseaseorAttack']) == 1:
                HeartDiseaseorAttack_Yes = 'checked'
            else:
                HeartDiseaseorAttack_No = 'checked'
            # PhysActivity
            PhysActivity_Yes = ''
            PhysActivity_No = ''
            if int(form_data['PhysActivity']) == 1:
                PhysActivity_Yes = 'checked'
            else:
                PhysActivity_No = 'checked'
            # Fruits
            Fruits_Yes = ''
            Fruits_No = ''
            if int(form_data['Fruits']) == 1:
                Fruits_Yes = 'checked'
            else:
                Fruits_No = 'checked'
            # Veggies
            Veggies_Yes = ''
            Veggies_No = ''
            if int(form_data['Veggies']) == 1:
                Veggies_Yes = 'checked'
            else:
                Veggies_No = 'checked'
            # HvyAlcoholConsump
            HvyAlcoholConsump_Yes = ''
            HvyAlcoholConsump_No = ''
            if int(form_data['HvyAlcoholConsump']) == 1:
                HvyAlcoholConsump_Yes = 'checked'
            else:
                HvyAlcoholConsump_No = 'checked'
            # AnyHealthcare
            AnyHealthcare_Yes = ''
            AnyHealthcare_No = ''
            if int(form_data['AnyHealthcare']) == 1:
                AnyHealthcare_Yes = 'checked'
            else:
                AnyHealthcare_No = 'checked'
            # NoDocbcCost
            NoDocbcCost_Yes = ''
            NoDocbcCost_No = ''
            if int(form_data['NoDocbcCost']) == 1:
                NoDocbcCost_Yes = 'checked'
            else:
                NoDocbcCost_No = 'checked'
            # Sex
            Male = ''
            Female = ''
            if int(form_data['Sex']) == 1:
                Male = 'checked'
            else:
                Female = 'checked'

            #menthlth
            MentHealth=int(form_data['MentHlth'])
            #physHlth
            PhysHealth=int(form_data['PhysHlth'])

            return render_template('index.html', Height=Height, Weight=Weight, HighBP_Yes=HighBP_Yes, HighBP_No=HighBP_No,
                            HighChol_Yes=HighChol_Yes, HighChol_No=HighChol_No,
                            CholCheck_Yes=CholCheck_Yes, CholCheck_No=CholCheck_No,
                            Smoker_Yes=Smoker_Yes, Smoker_No=Smoker_No,
                            Stroke_Yes=Stroke_Yes, Stroke_No=Stroke_No,
                            HeartDiseaseorAttack_Yes=HeartDiseaseorAttack_Yes, HeartDiseaseorAttack_No=HeartDiseaseorAttack_No,
                            PhysActivity_Yes=PhysActivity_Yes, PhysActivity_No=PhysActivity_No,
                            Veggies_Yes=Veggies_Yes, Veggies_No=Veggies_No,
                            Fruits_Yes=Fruits_Yes, Fruits_No=Fruits_No,
                            HvyAlcoholConsump_Yes=HvyAlcoholConsump_Yes, HvyAlcoholConsump_No=HvyAlcoholConsump_No,
                            AnyHealthcare_Yes=AnyHealthcare_Yes, AnyHealthcare_No=AnyHealthcare_No,
                            NoDocbcCost_Yes=NoDocbcCost_Yes, NoDocbcCost_No=NoDocbcCost_No,
                            GenHlth_0=GenHlth_0, GenHlth_1=GenHlth_1, GenHlth_2=GenHlth_2, GenHlth_3=GenHlth_3, GenHlth_4=GenHlth_4, GenHlth_5=GenHlth_5,
                            DiffWalk_Yes=DiffWalk_Yes, DiffWalk_No=DiffWalk_No,
                            Male=Male, Female=Female, MentHealth=MentHealth, PhysHealth=PhysHealth,
                            prediction=prediction)        

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)