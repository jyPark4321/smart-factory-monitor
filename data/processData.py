import random
from numpy.random import randint
from numpy.random import rand
import pandas as pd
import datetime
import time as moduletime
import numpy as np
from tqdm import tqdm
import sqlite3
import json

def processData(start_date, end_date):

    process_start = moduletime.time()

    # 데이터베이스에 연결
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 데이터 조회
    cursor.execute("SELECT * FROM data_input ORDER BY date DESC LIMIT 1")
    result = cursor.fetchone()

    # 데이터베이스 연결 종료
    conn.close()

    if result is None:
        print("데이터가 존재하지 않아 전처리 함수를 종료합니다.")
        return
    
    order_info = pd.read_json(result[1])
    order_info['time'] = order_info['time'].apply(lambda x: 
                                                  datetime.datetime.fromtimestamp(x/1000)
                                                  )
    machine_info = pd.read_json(result[2])
    
    print(order_info)

    time_range = {'start_date':start_date, 'end_date':end_date}
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    filtered_order_info = order_info[
        (order_info['time'] > start_date)
        & (order_info['time'] <= end_date)
    ]
    
    # 인덱스 재설정
    filtered_order_info = filtered_order_info.reset_index(drop=True)
    
    dataset = pd.merge(filtered_order_info, machine_info, on='item', how='inner')

    ###########################################################
    ##### [단계 5] 변수 생성
    ###########################################################


    # T = 생산해야 하는 기한의 날짜 집합
    # I = 생산해야 하는 item 종류
    # J = 사용 가능한 NC machine 종류
    T = list(set(dataset['time']))
    I = list(set(dataset['item']))
    J = list(set(dataset['machine']))
    

    # cit = 날짜 t에, item i가 미생산 될 때 발생하는 비용 (cost, c_i,t)
    # pit = 날짜 t에, item i가 긴급 생산이 필요한 경우 1, 그렇지 않으면 0 (urgent, p_i,t)
    # dit = 날짜 t에 item i마다 생산되어야 하는 요구량 (qty, d_i,t)
    # mijt = 날짜 t에 NC machine j가 item i를 생산할 수 있는 능력 (capacity, m_i,j,t)
    cit = dict() #c_i,t
    for i in I:
      for t in T:
        temp_dataset = dataset[
          (dataset['item']==i)
          &(dataset['time']==t)]
    
        if len(temp_dataset) != 0:
          value = list(set(temp_dataset['cost']))[0]
          cit[i, t] = value
        else:
          cit[i, t] =0
    
    pit = dict() #p_i,t
    for i in I:
      for t in T:
        temp_dataset = dataset[
          (dataset['item']==i)
          &(dataset['time']==t)]
    
        if len(temp_dataset) != 0:
          value = list(set(temp_dataset['urgent']))[0]
          pit[i, t] = value
        else:
          pit[i, t] = 0
    
    dit = dict() #d_i,t
    for i in I:
      for t in T:
        temp_dataset = dataset[
          (dataset['item']==i)
          &(dataset['time']==t)]
    
        if len(temp_dataset) != 0:
          value = list(set(temp_dataset['qty']))[0]
          dit[i, t] = value
        else:
          dit[i, t] = 0
    
    mijt = dict() #m_i,j,t
    for i in I:
      for j in J:
        temp_dataset = dataset[
          (dataset['item']==i)
          &(dataset['machine']==j)]
    
        if len(temp_dataset) !=0:
          value = list(set(temp_dataset['capacity']))[0]
          for t in T:
            mijt[i, j, t] = value
        else:
          for t in T:
            mijt[i, j, t] =0
    
    
    ###########################################################
    ##### [단계 6] 유전 알고리즘 구축
    ###########################################################
    
    ##### 세부함수 구축
    # generation_xijt() 함수는 목적함수를 최적화하기 위한 xijt 조합을 임의로 생성하
    # 는 함수이다. ‘random.uniform()’ 함수는 특정 값 사이 실수를 임의로 추출하는 함
    # 수이다. xijt는 0~1 사이 임의의 실숫값을 할당해야 하므로 ‘random.uniform(0,1)’
    # 을 사용하여 할당하였다. demand가 없는 변수에는 0을 할당하였다.
    def generation_xijt():
      xijt = {}
      for i in I:
        for j in J:
          for t in T:
            if dit[i, t] >0:
              xijt[i, j, t] = random.uniform(0, 1)
            else:
              xijt[i, j, t] =0
      xijt = decode(mijt, xijt)
      return xijt
    
    # 다음은 빠른 계산을 위한 utility 함수이다. 변수는 해석하기 쉬운 dictionary 자료
    # 형으로 생성했지만, crossover 또는 mutation과 같이 index를 이용하는 경우를 위
    # 해 dictionary 자료형에서 list 자료형으로 변경하는 함수 ‘dict2list()’와 list 자료형
    # 에서 dictionary 자료형으로 변경하는 함수 ‘list2dict()’를 작성하였다.
    def dict2list(xijt):
     return list(xijt.values())
    
    def list2dict(bitstring, type='xijt'):
      if type =='xijt':
        _keys = xijt_keys
      elif type =='mijt':
        _keys = mijt_keys
      for idx, value in enumerate(bitstring):
        xijt[_keys[idx]] = value
      return xijt
    
    # decode() 함수는 임의의 해인 xijt 조합 중 범위 밖의 값을 0으로 조정해주는 함수
    # 이다. mijt가 0인 것은 시간 t에, item i를 machine j로 만들 수 없다는 의미이므로
    # xijt 값을 0으로 할당 한다. decode() 함수는 이를 보정 해준다.
    def decode(mijt, xijt):
      for j in J:
        for t in T:
          for i in I:
            if mijt[i, j, t] == 0:
              xijt[i, j, t] = 0
      return xijt
    
    # objective() 함수는 임의의 해 조합인 xijt의 objective 값을 계산한다. 양의 u는 주
    # 어진 demand보다 적게 생산한 양이다. 음의 u는 주어진 demand보다 초과 생산한
    # 양이며, 이 경우 좀 더 큰 페널티를 주었다.
    def objective(xijt):
      uit = {}
      xijt = constraint_check(xijt) #[코드 26]에서 정의한 함수
      for i in I:
        for t in T:
          u = dit[i, t] - sum(round(xijt[i, j, t]*dit[i, t] )for j in J)
          if u >=0:
            uit[i, t] = u
          else:
            uit[i, t] = abs(u)*10000000
      objective = sum(uit[i, t] * cit[i, t] * pit[i, t] for i in I for t in T)
      return objective
    
    # constraint_check() 은 제약조건 관련 함수이다. 기계가 하루동안 총 생산할 수 있는
    # 시간은 600분이며, 한 기계에 할당된 생산량이 600분 안에 만들 수 없다면 해당 아이
    # 템을 생산하지 않게 할당하는 함수이다.
    def constraint_check(xijt):
      for j in J:
        for t in T:
          check_value = sum(mijt[i, j, t]*round(xijt[i, j, t]*dit[i, t]) for i in I) <= 600
          if check_value == False:
            for i in I:
              xijt[i, j, t] = 0
      return xijt
    
    # ‘selection()’ 함수는 임의의 해 조합을 crossover 하기 위해 한 세대 조합해 중 가장
    # 좋은 성능을 가진 조합을 찾는 과정이다. ‘k’는 임의의 해에서 crossover로 넘길 변수
    # 개수이며, 전체 임의의 해 조합(pop) 중 50%이다. 본 가이드북에서는 토너먼트 방법
    # 을 사용하였으며, 이는 임의로 뽑은 임의의 해 중 가장 좋은 해만을 다음으로 넘기는
    # 것이다.
    def selection(pop, scores): #n_pop은 한 세대를 구성하는 염색체 수이며, 하이퍼파라미터 값
      k = round(n_pop*0.5)
      selection_ix = randint(len(pop))
      for ix in randint(0, len(pop), k-1):
        if scores[ix] < scores[selection_ix]:
          selection_ix = ix
      return pop[selection_ix]
    
    # ‘crossover()’는 ‘select()’ 된 함수에서 두 쌍을 선택, 특정 비율 (r_cross)만큼을 교차
    # 시켜 재조합하여 새로운 임의의 해를 만드는 함수이다.
    # 본 가이드북 문제는 특정 i, j, t 만이 정수를 해를 가질 수 있으므로 (임의의 item i는
    # 특정 날짜 t, 특정 machine j로만 생산 가능) 임의로 교차를 할 수 없다. 따라서 해를
    # 가질 수 있는 index를 vaild_index 변수에 저장하고 (crossover_(1)), 이 중 특정 비
    # 율만큼 index를 선택하여 교차시킨다. (crossover_(2))
    def crossover(p1, p2, r_cross):
      p1 = dict2list(p1)
      p2 = dict2list(p2)
      c1, c2 = p1.copy(), p2.copy()
      if rand() < r_cross:
        base_bitstring = dict2list(mijt)
        # crossover_(1)
        valid_index = []
        for i in range(len(base_bitstring)):
          if base_bitstring[i]>0:
            valid_index.append(i)
    
        n = round(r_cross*len(valid_index))
        pt_0 = random.sample(valid_index, n)
        pt_1 = list(set(valid_index)-set(pt_0))
        # crossover_(2)
        for i in pt_0:
          c1[i] = p2[i]
          c2[i] = p1[i]
        for i in pt_1:
          c1[i] = p2[i]
          c2[i] = p1[i]
      return [c1, c2]
    
    # ‘mutation()’ 함수는 ‘crossover()’ 이후 특정 비율 (r_mut) 만큼 새로운 임의의 해
    # (mutation_(1))로 교체(mutation_(2))하는 함수로 다양한 임의 해를 생성하는 역할
    # 을 한다.
    def mutation(bitstring, r_mut):
      for i in range(len(bitstring)):
        if rand() < r_mut:
          base_bitstring = dict2list(mijt)
          valid_index = []
          for i in range(len(base_bitstring)):
            if base_bitstring[i]>0:
              valid_index.append(i)
    
      n = round(r_mut*len(valid_index))
      # mutation_(1)
      pt_0 = random.sample(valid_index, n)
      # mutation_(2)
      for i in pt_0:
        bitstring[i] = random.uniform(0, 1)
    
    # ‘genetic_algorithm()’ 함수는 유전 알고리즘이며, 앞서 정의한 함수를 활용한다. 본
    # 알고리즘은 100세대 이상 개선이 없다면 종료한다. (stop_rule)
    def genetic_algorithm(bounds, n_iter, n_pop, r_cross, r_mut):
      # utility
      log = []
      log_detail = []
      best_gen =0
      # GA algorithm
      pop = [generation_xijt() for _ in range(n_pop)]
      best, best_eval = decode(mijt, pop[0]), objective(decode(mijt, pop[0]))
      print(best_eval)
      for gen in tqdm(range(n_iter)):
        decoded = [decode(mijt, p) for p in pop]
        # 임의의 해 집합에서 목적함수 값 계산하기
        scores = [objective(d) for d in decoded]
        # 가장 좋은 해 선택
        for i in range(n_pop):
          if scores[i] < best_eval:
            best, best_eval = pop[i], scores[i]
            print(f'>best! {gen}, {scores[i]}')
            best_gen = gen
          else:
            # stop_rule
            if gen - best_gen >100:
              print('stop')
              return [best, best_eval, log, log_detail]
        # 부모 해 집합 선택
        selected = [selection(pop, scores) for _ in range(n_pop)]
        log_detail.append([gen, objective(selected[0])])
        children = list()
        for i in range(0, n_pop, 2):
          p1, p2 = selected[i], selected[i+1]
          for c in crossover(p1, p2, r_cross):
            mutation(c, r_mut)
            children.append(list2dict(c))
        pop = children
        log.append([gen, best_eval])
      return [best, best_eval, log, log_detail]
    
    ##### 파라미터 할당
    # 유전 알고리즘은 [표 8]에서 설명한 하이퍼파라미터를 설정해야 하며, 문제 유형에 따
    # 라, 계산 환경에 따라 사용자가 설정해야 한다. 또한, 파라미터 조합에 따라 최종 성능
    # 이 달라질 수 있어 주의해야 한다. 다음은 하이퍼파라미터 추천 범위이다.
    hyper_parameters = pd.DataFrame({'index':['index_1', 'index_2', 'index_3', 'index_4', 
                                              'index_5', 'index_6', 'index_7', 'index_8'],
                                     'n_iter':[200, 200, 200, 200, 200, 200, 200, 200],
                                     'n_pop':[10, 20, 40, 20, 20, 20, 20, 20],
                                     'r_cross':[0.4, 0.4, 0.4, 0.1, 0.2, 0.3, 0.4, 0.4],
                                     'r_mut':[0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.1, 0.6]
                                     })
    hyper_parameters['objective'] = np.nan
    hyper_parameters['time'] = np.nan
    
    # 모든 하이퍼파라미터 조합을 실험하여 가장 좋은 조합을 선택한다. 실험을 위한 코
    # 드는 다음과 같다. ‘len(hyper_parameters)’은 hyper_parameters 데이터프레임의
    # row 수이며, 모든 경우에 대해 반복 실험한다.
    # GA는 임의성이 바탕이 되므로 매번 결과는 달라질 수 있다.
    log_list = []
    min_score = 10000000000000000
    min_index = 0
    for i in range(len(hyper_parameters)):
      parameter = hyper_parameters.iloc[i]
      index_nm = parameter['index']
      print(f'{index_nm}')
      start=datetime.datetime.now()
      xijt = generation_xijt()
      xijt_keys = list(xijt.keys())
      mijt_keys = list(mijt.keys())
      # number of generations
      n_iter = parameter['n_iter']
      # define the population size
      n_pop = parameter['n_pop']
      # crossover rate
      r_cross = parameter['r_cross']
      # mutation rate
      r_mut = parameter['r_mut']
      best, score, log, log_detail = genetic_algorithm(mijt, n_iter, n_pop, r_cross, r_mut)
      time = datetime.datetime.now()-start
      hyper_parameters.loc[i, 'time'] = time
      hyper_parameters.loc[i, 'objective'] = score
      log_list.append(log)
      if (score < min_score):
        min_score = score
        min_index = i
    
    print("used index = " + str(min_index) + "\n")
    
    ###########################################################
    ##### [단계 7] 유전 알고리즘 실행
    ###########################################################
    
    xijt =generation_xijt()
    xijt_keys =list(xijt.keys())
    mijt_keys =list(mijt.keys())
    # 반복할 세대 수, 유전 알고리즘을 반복할 수
    n_iter = hyper_parameters.loc[min_index, 'n_iter']
    # 한 세대를 구성하는 염색체 수
    n_pop = hyper_parameters.loc[min_index, 'n_pop']
    # 교배율, 부모 염색체로부터 교배할 유전자 비율
    r_cross = hyper_parameters.loc[min_index, 'r_cross']
    # 변이율, 새로 생긴 염색체에서 임의로 변경할 유전자 비율
    r_mut = hyper_parameters.loc[min_index, 'r_mut']
    
    best, score, log, log_detail = genetic_algorithm(mijt, n_iter, n_pop, r_cross, r_mut)
    print('Done!')
    # plt.plot(list(pd.DataFrame(log)[1]))
    # plt.title(f'Result(x axis: generation, y axis: penalty))')
    
    
    ###########################################################
    ##### [단계 8] 결과 분석 및 해석
    ###########################################################
    
    # 유전 알고리즘으로 도출된 모든 해 확인은 다음과 같다.
    # to_csv() 함수는 데이터 프레임 자료형 데이터를 저장한다.
    # 유전 알고리즘의 최적해 결과는 매번 달라질 수 있다.
    solution_ = dict()
    xijt = decode(mijt, xijt)
    for i in I:
      for j in J:
        for t in T:
          solution_[i, j, t] = round(best[i, j, t]*dit[i, t])
    sol = pd.DataFrame.from_dict(solution_, orient='index').reset_index()
    sol.columns = ['(item, machine, time)','qty']
    # sol.to_csv('GA_solution.csv', index=False)
    # sol = pd.read_csv('GA_solution.csv')
    sol = sol[sol['qty']>0]
    print(sol)

    process_end = moduletime.time()
    process_time = str(round(process_end - process_start, 2))
    print("작업 시간:", process_time)
    
    ###### 데이터 저장
    
    # 데이터베이스에 연결
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 테이블이 없을 경우 생성
    cursor.execute("CREATE TABLE IF NOT EXISTS data_output (date TEXT, time_range TEXT, process_time TEXT, data TEXT, sol TEXT)")
    
    # 저장할 데이터
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timerange_json = json.dumps(time_range)
    
    dataset['time'] = dataset['time'].apply(lambda x: str(x))
    data_json = dataset.to_json()
    
    
    sol['(item, machine, time)'] = sol['(item, machine, time)'].apply(lambda x: (x[0], x[1], str(x[2])))
    sol_json = sol.to_json()
    
    # 삽입
    cursor.execute("INSERT INTO data_output (date, time_range, process_time, data, sol) VALUES (?, ?, ?, ?, ?)",
                   (date, timerange_json, process_time, data_json, sol_json))
    
    # 변경사항 저장 및 연결 종료
    conn.commit()
    conn.close()
    
    print('\n\n데이터 전처리 완료\n\n')

if (__name__ == '__main__'):
    processData('2021-01-01', '2021-06-01')