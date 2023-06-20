###########################################################
##### [단계 1] 라이브러리/데이터 불러오기
###########################################################

##### 라이브러리
import pandas as pd
import datetime
import sqlite3
import json
import os

def saveDataSet():
  ##### 데이터 불러오기
  os.chdir(os.path.dirname(__file__))
  machine_info = pd.read_csv('machine_info.csv', encoding='cp949')
  order_info = pd.read_csv('order_info.csv', encoding='cp949')

  ##### 데이터 전처리
  # 전처리 (1) coulmn name 변경
  order_info =order_info.rename(columns={
    '영업납기':'time',
    '중산도면':'item',
    '단가':'cost',
    '수량':'qty',
    '선급':'urgent'
  })
  machine_info =machine_info.rename(columns={
    'JSDWG':'item',
    'MCNO':'machine',
    'AVG_CT':'capacity'
  })

  # 전처리 (2) 분석을 위한 데이터 처리
  # urgent의 빈 데이터를 0으로, 비어있지 않으면 1
  order_info['urgent']=order_info['urgent'].fillna(0)
  for i in range(len(order_info)):
    if order_info.loc[i,'urgent']!=0:
      order_info.loc[i,'urgent']=1

  # 전처리 (3) time(영업납기) type 부여
  order_info['time'] = order_info['time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))

  ###########################################################
  ##### [단계 2] 데이터 유효성 검증
  ##### 부록 4 (61페이지) 참고
  ###########################################################

  # 품질 지수 저장할 딕셔너리, 무결성 계산을 위한 결함 개수 저장할 변수
  data_quality = {}
  defect_o = 0
  defect_m = 0

  # 1. 완전성 품질 지수 = ((1-결측치)/전체 데이터 수) * 100
  perc =30
  df_set ={'order_info':order_info,'machine_info':machine_info}
  for df_name in list(df_set):
      print(f'DataFrame name: order_info')
      df = df_set[df_name]
      # Null 값이 30% 이상인 데이터들은 데이터의 완전성이 떨어지기 때문에 열별 Null 값의 비율을 확인하여 삭제한다.
      # 이 데이터는 30%를 넘는 열이 존재하지 않으므로 열을 제거하지 않는다. 
      print('[step 1-1]')
      print(round(df.isnull().sum()/len(df)*100,2))
      print('[step 1-2]')
      print(df.isnull().sum()/len(df)*100>perc)
      # 데이터의 결측치를 확인하기 위하여 ‘isnull()’ 함수를 사용한 뒤, ‘sum()’ 함수를 이용하여 총 결측치 개수를 구한다. 
      print('[step 2-1]')
      print(df.isnull().head())
      print('[step 2-2]')
      print(df.isnull().sum())
      print('[step 2-3]')
      cmpt_len = df.isnull().sum().sum()
      print(cmpt_len)

      if(cmpt_len > 0):
          if (df_name == 'order_info'):
              defect_o += 1
          else:
              defect_m += 1
  # 구한 결측치의 개수를 이용하여 완전성 품질 지수를 구한다.
  completeness = (1-cmpt_len/len(df))*100
  print("결측치 = %d개 \n완전성 지수 : %.2f%% \n"%(cmpt_len, completeness))
  data_quality['completeness'] = completeness


  # 2. 유일성 품질 지수 = ((유일한 데이터 수)/전체 데이터 수) * 100
  # 'value_counts()’ 함수를 이용하여 key 값들 개수를 확인한다. 개수가 큰 순서로 기본 정렬된다. 'reset_index()' 함수는 데이터 프레임 인덱스를 재부여한다.
  check_unique = order_info[
    ['time','item','urgent']
    ].value_counts().reset_index()

  check_unique = machine_info[
    ['item','machine']
    ].value_counts().reset_index()
  # key 값들 개수로 정렬했을 때, 1 이상인 행 개수 비율의 평균이 유일성 품질 지수다.
  perc_check_unique_item_urgent_info = round(
    (len(check_unique)-len(check_unique[check_unique[0]>1]))
    /len(check_unique)*100,2)
  if(perc_check_unique_item_urgent_info < 100):
    defect_o += 1

  perc_check_unique_machine_info = round(
    (len(check_unique)-len(check_unique[check_unique[0]>1]))
    /len(check_unique)*100,2)
  if(perc_check_unique_machine_info < 100):
    defect_m += 1

  print(f'The percentage of uniqueness for time<->item<->cost<->urgent : {perc_check_unique_item_urgent_info}')
  print(f'The percentage of uniqueness for item<->machine : {perc_check_unique_machine_info}')
  uniqueness = (perc_check_unique_machine_info+perc_check_unique_item_urgent_info)/2
  print("유일성 지수 : %.2f%% \n"%(uniqueness))
  data_quality['uniqueness'] = uniqueness


  # 3. 유효성 품질 지수 = (유효성 만족 데이터 수/전체 데이터 수)*100
  print('order_info case')
  df = order_info
  c_lb =df['cost']>=0
  c_ub =df['cost']<=1000000
  q_lb =df['qty']>=0
  q_ub =df['qty']<=1000000
  u_lb =df['urgent']>=0
  u_ub =df['urgent']<=1
  vald_df =df[c_lb &c_ub &q_lb &q_ub &u_lb &u_ub]
  print(f'[Step 1] 데이터 범위를 벗어난 데이터 수: {len(df)-len(vald_df)}')
  d0 =pd.Timestamp(datetime.date(2021,1,31)) 
  d1 =pd.Timestamp(datetime.date(2021,10,31)) 
  con1 =vald_df['time']>=d0
  con2 =vald_df['time']<=d1
  vald_df =vald_df[con1&con2]
  print(f'[Step 2] 수집된 날짜를 벗어나는 데이터 수: {len(df)-len(vald_df)}')
  vald_df['time']=vald_df['time'].apply(lambda x:isinstance(x,datetime.datetime))
  vald_df['item']=vald_df['item'].apply(lambda x:isinstance(x,str))
  vald_df['cost']=vald_df['cost'].apply(lambda x:isinstance(x,int))
  vald_df['qty']=vald_df['qty'].apply(lambda x:isinstance(x,int))
  vald_df['urgent']=vald_df['urgent'].apply(lambda x:isinstance(x,int))
  print(f'[Step 3] 데이터 형식을 벗어나는 데이터 수: {len(df)-len(vald_df)}')
  vald_df[
    (vald_df['time']==True)
    &(vald_df['item']==True)
    &(vald_df['cost']==True)
    &(vald_df['qty']==True)
    &(vald_df['urgent']==True)
    ]
  vald_len =len(vald_df)
  item_vald =vald_len/len(df)*100
  print("order_info 유효성 지수 : %.2f%% "%(item_vald))
  if(item_vald < 100):
    defect_o += 1

  print('machine_info case')
  df = machine_info
  cap_lb =df['capacity']>=0
  cap_ub =df['capacity']<=1000000
  vald_df =df[cap_ub &cap_lb]
  print(f'[Step 1] 데이터 범위를 벗어난 데이터 수: {len(df)-len(vald_df)}')
  vald_df['item']=vald_df['item'].apply(lambda x:isinstance(x,str))
  vald_df['machine']=vald_df['machine'].apply(lambda x:isinstance(x,str))
  vald_df['capacity']=vald_df['capacity'].apply(lambda x:float(x)if isinstance(x,int)==True else x)
  vald_df['capacity']=vald_df['capacity'].apply(lambda x:isinstance(x,float))
  print(f'[Step 3] 데이터 형식을 벗어나는 데이터 수: {len(df)-len(vald_df)}')
  vald_df[
    (vald_df['item']==True)
    &(vald_df['machine']==True)
    &(vald_df['capacity']==True)
    ]
  vald_len =len(vald_df)
  machine_vald =vald_len/len(df)*100
  print("machine_info 유효성 지수 : %.2f%% "%(machine_vald))
  if(machine_vald < 100):
    defect_m += 1

  validity = (item_vald +machine_vald)/2
  print("유효성 지수 : %.2f%% \n"%(validity))
  data_quality['validity'] = validity

  # 4. 일관성 품질 지수 = (일관성 만족 데이터수/전체 데이터 수)*100
  # order_info만 계산
  # order_info의 모든 'item'은 machine_info 'item' 중 하나여야 한다
  df = order_info
  vald_df = df[['item']].copy()
  vald_df['check'] = vald_df['item'].isin(set(machine_info['item']))
  consistency = sum(vald_df['check'])/len(df)*100
  if (consistency < 100):
    defect_o += 1

  print("일관성 지수 : %.2f%% "%(consistency))
  data_quality['consistency'] = consistency

  # 5. 정확성 품질 지수 = (1-(정확성 위배 데이터 수/전체 데이터 수))*100
  # 모든 열값은 독립적이므로 정확성 지수를 확인하지 않음
  print("정확성 지수 : 100.00% ")
  data_quality['accuracy'] = 100.

  # 6. 무결성 품질지수 = (1-(유일성, 유효성, 일관성 지수중 100%가 아닌 지수 개수 / 3))*100
  # order_info 데이터는 세 가지 지수중 유일성 지수가 100%를 만족하지 못하므로 (99.16%) 
  # 무결성 품질 지수는 66.66%이다. machine_info의 경우, 일관성 지수는 고려하지 않는 대
  # 상이며, 유일성과 유효성 지수는 모두 100%이므로 무결성 품질 지수는 100%이다. order_
  # info와 machin_info의 평균 무결성 품질 지수는 83.35%이다.
  i_o = (1-(defect_o/3)) * 50
  i_m = (1-(defect_m/2)) * 50
  integrity = i_o + i_m
  data_quality['integrity'] = round(integrity)
  print("무결성 지수 : %.2f%% "%(integrity))


  # 가중치 지수 = 품질 지수 * 가중치
  # 데이터 품질 지수 = ∑ 가중치 지수
  quality_total = (data_quality['completeness']*0.6) + (data_quality['uniqueness']*0.1) + (data_quality['validity']*0.1) + data_quality['accuracy']*0.1 + (data_quality['integrity']*0.1)
  data_quality['total'] = quality_total
  print("데이터 품질 지수 : %.2f%% "%(quality_total))



  ###########################################################
  ##### [단계 3] 데이터 종류 및 개수 확인
  ###########################################################
  # 변환하는 과정이 없으므로 생략


  ###########################################################
  ##### [단계 4] 데이터 정제 (전처리)
  ###########################################################


  ##### 불필요한 데이터 제거

  # '.dropna() 함수는 값이 없는 행 (axis=0) 또는 열 (axis=1)을 제거해 주는 함수이다. 
  # inplace=True 옵션은 따로 데이터프레임을 지정해 저장하지 않고 바로 적용된다. 본 
  # 분석에서는 모든 데이터 (machine_info.csv, order_info.csv)에 대해 값이 없는 행을 
  # 모두 제거하였다.
  n_before_preprocess =len(machine_info)
  machine_info.dropna(axis=0,inplace=True)
  n_after_preprocess =len(machine_info)
  print(f'machine_info : nan 값 제거 ({n_before_preprocess} row --> {n_after_preprocess} row,\
  {round(((n_before_preprocess-n_after_preprocess)/n_before_preprocess*100),3)}% 삭제)')

  n_before_preprocess =len(order_info)
  order_info =order_info[['time','item','cost','qty','urgent']]
  order_info.dropna(axis=0,inplace=True)
  n_after_preprocess =len(order_info)
  print(f'order_info : nan 값 제거 ({n_before_preprocess} row --> {n_after_preprocess} row,\
  {round(((n_before_preprocess-n_after_preprocess)/n_before_preprocess*100),3)}% 삭제)')

  # 같은 날 같은 item을 중복으로 주문한 결과를 합쳤다.
  order_info = order_info.groupby(['time','item','cost','urgent']).sum().reset_index()


  ###### 데이터 저장

  # 데이터베이스에 연결
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()

  # 테이블이 없을 경우 생성
  cursor.execute("CREATE TABLE IF NOT EXISTS data_input (date TEXT, order_info TEXT, machine_info TEXT, quality TEXT)")

  # 저장할 데이터
  date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  order_info_json = order_info.to_json()
  machine_info_json = machine_info.to_json()
  quality_json = json.dumps(data_quality)
  
  # 삽입
  cursor.execute("INSERT INTO data_input (date, order_info, machine_info, quality) VALUES (?, ?, ?, ?)", (date, order_info_json, machine_info_json, quality_json))

  # 변경사항 저장 및 연결 종료
  conn.commit()
  conn.close()
  
  print('\n\n입력 데이터 저장 완료\n\n')


if (__name__ == '__main__'):
    saveDataSet()
    