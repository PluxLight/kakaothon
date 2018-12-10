import random
import psycopg2
import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup


def key_insert(u_key, reque): # 기존에 있던것은 depth=2로 업데이트 -> 유저가 응답한 반응은 새 튜플에 넣고
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("key_Insert Error")
        return 0

    cur = conn.cursor()
    del_str = "delete from user_key where depth=2 and key='" + u_key + "';"
    insert_str = "insert into user_key values ('" + u_key +"', '" + reque +"', 1);"
    update_str = "update user_key set depth='2' where key='" + u_key + "';"
    try: #기존에 값이 있던 경우
        cur.execute(del_str)
        conn.commit()
        cur.execute(update_str)
        conn.commit()
        cur.execute(insert_str)
        conn.commit()

    except: #첫 사용시 값이 없는 경우 등
        cur.execute(insert_str)
        conn.commit()

    cur.close()
    conn.close()

    return 0

def pre_value(u_key):
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("Pre_Value Error")
        return 0

    cur = conn.cursor()
    sql_str = "select request from user_key where key='" + u_key + "';"
    try: #기존에 값이 있던 경우
        cur.execute(sql_str)

        result = cur.fetchall()

        return result[1][0]

    except: #첫 사용시 값이 없는 경우
        return '0'

def pre_pre_value(u_key):
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("Pre_Pre_Value Error")
        return 0

    cur = conn.cursor()
    sql_str = "select request from user_key where key='" + u_key + "';"
    try: #기존에 값이 있던 경우
        cur.execute(sql_str)

        result = cur.fetchall()

        return result[0][0]

    except: #첫 사용시 값이 없는 경우
        return '0'

def star_point(star, pre_text, pre_pre_text): #사용자가 보낸 별점을 db에 등록
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("Star_point Error")
        return 0

    #print(pre_text, pre_pre_text)

    if pre_text == "조식" and pre_pre_text == "채움관&이룸관":
        position = 'cheaum_morning'
    elif pre_text == '중식' and pre_pre_text == '채움관&이룸관':
        position = 'cheaum_lunch'
    elif pre_text == '석식' and pre_pre_text == '채움관&이룸관':
        position = 'cheaum_dinner'
    elif pre_text == '조식' and pre_pre_text == '기숙사':
        position = 'domitori_morning'
    elif pre_text == '중식' and pre_pre_text == '기숙사':
        position = 'domitori_lunch'
    elif pre_text == '석식' and pre_pre_text == '기숙사':
        position = 'domitori_dinner'
    else:
        return 0


    cur = conn.cursor()
    update_str = "update star_point set point=point + " + str(star) + ", count=count + 1 where position='" + position + "';"

    cur.execute(update_str)
    conn.commit()

    cur.close()
    conn.close()

    return 0

def trans_star(sum, cnt):
    if cnt == 0:
        pass
    else:
        sum = sum / cnt

    if sum == 5 or sum > 4.0:
        star_str = '★★★★★'
        return star_str
    elif sum <= 4.0 and sum > 3.0:
        star_str = '★★★★☆'
        return star_str
    elif sum <= 3.0 and sum > 2.0:
        star_str = '★★★☆☆'
        return star_str
    elif sum <= 2.0 and sum > 1.0:
        star_str = '★★☆☆☆'
        return star_str
    elif sum <= 1.0 and sum > 0.0:
        star_str = '★☆☆☆☆'
        return star_str
    else:
        star_str = '☆☆☆☆☆'
        return star_str

def star_cnt(position): #사용자가 식단정보 요청시 별점정보도 같이 보낼때 숫자형태를 특수문자 별로 변환  별점 주기에 참여한 사람들 숫자도 보내기
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("star_cnt Error")
        return 0

    if position == "채움관" or position == "이룸관":
        position = 'cheaum'
    elif position == '기숙사':
        position = 'domitori'
    else:
        position = 'none'

    cur = conn.cursor()
    sql_str = "select point, count from star_point where position like '%" + position + "%' order by position desc;"

    cur.execute(sql_str)
    result = cur.fetchall()

    breakfast_star = result[0][0]
    breakfast_cnt = result[0][1]

    lunch_star = result[1][0]
    lunch_cnt = result[1][1]

    dinner_star = result[2][0]
    dinner_cnt = result[2][1]

    breakfast_star = trans_star(breakfast_star, breakfast_cnt)
    lunch_star = trans_star(lunch_star, breakfast_cnt)
    dinner_star = trans_star(dinner_star, breakfast_cnt)

    return breakfast_star, breakfast_cnt, lunch_star, lunch_cnt, dinner_star, dinner_cnt

def meal_exist(position, day):

    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("meal_exist Error")
        return 0

    day_db_h = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일(다음주)']  # DB 텍스트에 넣을 요일 문자 리스트

    day = day_db_h[day]

    cur = conn.cursor()
    sql_str = "select breakfast, lunch, dinner from school_menu where place='%s' and day='%s';"%(position, day)
    cur.execute(sql_str)
    result = cur.fetchall()

    breakfast_exist = result[0][0]
    lunch_exist = result[0][1]
    dinner_exist = result[0][2]

    return breakfast_exist, lunch_exist, dinner_exist

def star_reset(): #윈도우 스케줄러에 등록해서 매 정각마다 별점과 참여한 사람 수를 초기화, 투표 참여자도 초기화
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("Star_Reset Error")
        return 0

    cur = conn.cursor()
    update_str = "update star_point set point=0, count=0;"

    cur.execute(update_str)
    conn.commit()

    update_str = "update star_overlap set overlap_check=0;"

    cur.execute(update_str)
    conn.commit()

    cur.close()
    conn.close()

def overlap_check(u_key, pre_text,pre_pre_text):
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("Overlap_Check Error")
        return 0

    if pre_text == "조식" and pre_pre_text == "채움관&이룸관":
        position = 'cheaum_morning'
    elif pre_text == '중식' and pre_pre_text == '채움관&이룸관':
        position = 'cheaum_lunch'
    elif pre_text == '석식' and pre_pre_text == '채움관&이룸관':
        position = 'cheaum_dinner'
    elif pre_text == '조식' and pre_pre_text == '기숙사':
        position = 'domitori_morning'
    elif pre_text == '중식' and pre_pre_text == '기숙사':
        position = 'domitori_lunch'
    elif pre_text == '석식' and pre_pre_text == '기숙사':
        position = 'domitori_dinner'
    else:
        position = 'none'

    cur = conn.cursor()
    sql_str = "select overlap_check from star_overlap where userkey='" + u_key + "' and position='" + position +"';"

    cur.execute(sql_str)
    check_int = cur.fetchall()
    try:
        check_int = int(check_int[0][0])
        print(check_int)
    except:
        check_int = 0


    if check_int == 0: #투표 당일날 해당 항목에 투표를 한 번도 안한경우
        #update_str = "update star_overlap set overlap_check=1 where userkey='" + u_key + "' and position='" + position +"';"
        update_str = "insert into star_overlap values ('" + u_key + "', '" + position + "', 1)"
        cur.execute(update_str)
        conn.commit()

        cur.close()
        conn.close()

        return 0
    else: #투표 당일날 해당 항목에 투표한 경우
        return 1

def moms_db(moms_type):
    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("moms_db Error")
        return 0

    cur = conn.cursor()

    str_sql = "select * from moms where note='%s';"%moms_type

    cur.execute(str_sql)

    results = cur.fetchall()

    if moms_type == '버거':
        moms_data = '메뉴 / 단품가격 / 세트가격\n'
        for result in results:
            moms_data += str(result[0]) + ' / ' + str(result[1]) + ' / ' + str(result[2]) + '\n'
    else:
        moms_data = '메뉴 / 가격\n'
        for result in results:
            moms_data += str(result[0]) + ' ' + str(result[1]) + '\n'

    return moms_data

def school_menu_delete():
    conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    cur = conn.cursor()
    sql_str = "delete from school_menu;"
    cur.execute(sql_str)
    conn.commit()

def db_upload(place, upload_data, dow, morning, lunch, dinner):
    conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    cur = conn.cursor()
    sql_str = "insert into school_menu values ('%s', '%s', '%s', %r, %r, %r);" % (
    place, upload_data, dow, morning, lunch, dinner)
    cur.execute(sql_str)
    conn.commit()

def exist_check(morning, lunch, dinner): #조식, 중식, 석식 식단이 있는지 판단한다 / db에 업로드 할 때 사용
    if morning > 3:
        morning = True
    else:
        morning = False

    if lunch > 3:
        lunch = True
    else:
        lunch = False

    if dinner > 3:
        dinner = True
    else:
        dinner = False

    return morning, lunch, dinner

def menu_sum(breakfast, lunch, dinner):
    #print(breakfast, lunch, dinner)

    sum = ''
    for i in breakfast:
        sum += str(i) + '\n'
    breakfast = sum

    sum = ''
    for i in lunch:
        sum += str(i) + '\n'
        lunch = sum

    sum = ''
    for i in dinner:
        sum += str(i) + '\n'
        dinner = sum

    return breakfast, lunch, dinner

def domitori_create(): #이번주 기숙사 식단 DB생성
    url = 'http://dorm.andong.ac.kr/2014/food_menu/food_menu.htm'

    day_db_h = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

    day_of_week = dt.datetime.today().weekday() #요일 반환 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    now = dt.datetime.now() #현재 날짜 값
    standard_day = now - dt.timedelta(days=day_of_week) #함수가 실행된 시점에서 월요일의 날짜를 가져온다 #현재 날짜에서 현재 날짜의 값(weekday 반환 값)을 빼서 월요일의 날짜로 만듦

    cafe_table = pd.read_html(url)[0]
    cafe_table = cafe_table.fillna('없음')

    for i in range(0, 7):
        exact_day = standard_day + dt.timedelta(days=i)
        nowDate = str(exact_day.strftime('%Y-%m-%d'))

        breakfast = cafe_table[1][i+3]
        lunch = cafe_table[2][i+3]
        dinner = cafe_table[3][i+3]

        breakfast = breakfast.split(' ')
        lunch = lunch.split(' ')
        dinner = dinner.split(' ')

        em, el, ed = exist_check(len(breakfast), len(lunch), len(dinner))

        breakfast, lunch, dinner = menu_sum(breakfast, lunch, dinner)

        menu_text = nowDate + ' ' + day_db_h[i] + '\n<----------조식---------->\n식사시간 07:30~09:00\n' + breakfast + \
                    '\n<----------중식---------->\n식사시간 12:00~13:30\n' + lunch + \
                    '\n<----------석식---------->\n식사시간 18:00~19:30\n' + dinner

        db_upload('기숙사', menu_text, day_db_h[i], em, el, ed)

    tomorrow = now + dt.timedelta(days=7)  # 오늘 기준으로 +7일
    day_of_week = dt.datetime.today().weekday()  # 오늘 날짜의 요일을 숫자로 변환 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    tomorrow = tomorrow - dt.timedelta(days=day_of_week)  # 오늘 기준으로 다음주에서 오늘의 요일 값만큼 빼서 다음주 월요일이 도출
    toDate = str(tomorrow.strftime('%Y-%m-%d'))  # 도출된 값을 지정된 형식으로 문자열 포맷

    nowYearDate = str(tomorrow.strftime('%Y'))
    nowMonthDate = str(tomorrow.strftime('%m'))
    toDayDate = str(tomorrow.strftime('%d'))

    url = 'http://dorm.andong.ac.kr/2014/food_menu/food_menu.htm?year=' + nowYearDate + '&month=' + nowMonthDate + '&day=' + toDayDate

    cafe_table = pd.read_html(url)[0]
    cafe_table = cafe_table.fillna('없음')

    breakfast = cafe_table[1][3]
    lunch = cafe_table[2][3]
    dinner = cafe_table[3][3]

    breakfast = breakfast.split(' ')
    lunch = lunch.split(' ')
    dinner = dinner.split(' ')

    em, el, ed = exist_check(len(breakfast), len(lunch), len(dinner))

    breakfast, lunch, dinner = menu_sum(breakfast, lunch, dinner)

    menu_text = toDate + ' ' + '월요일' + '\n<----------조식---------->\n' + breakfast + \
                '\n<----------중식---------->\n식사시간 11:50~13:30\n' + lunch + \
                '\n<----------석식---------->\n식사시간 16:50~18:30\n' + dinner

    db_upload('기숙사', menu_text, '월요일(다음주)', em, el, ed)

def cheaum_create(): #이번주 채움관 식단 DB생성(생성 요일 무관하게 생성한 날 기준의 주간+다음주 월요일까지)

    day_db_sql = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일(다음주)'] #sql_str에 넣을 요일 문자 리스트
    day_db_menu = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일'] #menu_text에 넣을 요일 문자 리스트

    day_of_week = dt.datetime.today().weekday() #요일 반환 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    now = dt.datetime.now() #현재 날짜 값
    standard_day = now - dt.timedelta(days=day_of_week) #함수가 실행된 시점에서 월요일의 날짜를 가져온다 #현재 날짜에서 현재 날짜의 값(weekday 반환 값)을 빼서 월요일의 날짜로 만듦

    for i in range(0, 8):
        cheaum_url = 'http://www.andong.ac.kr/main/module/foodMenu/view.do?manage_idx=21&memo5=' #채움관 식단 정보가 있는 url(날짜 빠짐)
        exact_day = standard_day + dt.timedelta(days=i)
        nowDate = str(exact_day.strftime('%Y-%m-%d'))
        cheaum_url = cheaum_url + nowDate

        req = requests.get(cheaum_url)
        html = req.text
        soup = BeautifulSoup(html, 'lxml')

        soup = str(soup)

        if '정보가 없습니다' in soup:
            soup = BeautifulSoup(html, 'lxml')
            check_chaeum = soup.find_all('dt')
            menu_text = str(check_chaeum[0]).replace('<dt style="width:100%; text-align:center;">', "").replace("</dt>", "").split("<br/>")
            menu_text = nowDate + ' ' + day_db_menu[i] + '\n' + str(menu_text[0]) + '\n' + str(menu_text[1])
            db_upload('채움관', menu_text, day_db_sql[i], False, False, False)
        else:
            soup = BeautifulSoup(html, 'lxml')
            check_chaeum = soup.find_all('dd')

            breakfast = str(check_chaeum[0]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>") #Web에서 &기호 읽어들일때 amp; 라는 문장이 추가되어 제거하는 과정 추가
            lunch = str(check_chaeum[1]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>")
            dinner = str(check_chaeum[2]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>")

            em, el, ed = exist_check(len(breakfast), len(lunch), len(dinner))

            breakfast, lunch, dinner = menu_sum(breakfast, lunch, dinner)

            menu_text = nowDate + ' ' + day_db_menu[i] + '\n<----------조식---------->\n' + breakfast + \
                   '<----------중식---------->\n식사시간 11:50~13:30\n' + lunch + \
                   '<----------석식---------->\n식사시간 16:50~18:30\n' + dinner

            db_upload('채움관', menu_text, day_db_sql[i], em, el, ed)

def erum_create(): #이번주 채움관 식단 DB생성(생성 요일 무관하게 생성한 날 기준의 주간+다음주 월요일까지)

    day_db_sql = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일(다음주)'] #sql_str에 넣을 요일 문자 리스트
    day_db_menu = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일'] #menu_text에 넣을 요일 문자 리스트

    day_of_week = dt.datetime.today().weekday() #요일 반환 (0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일)
    now = dt.datetime.now() #현재 날짜 값
    standard_day = now - dt.timedelta(days=day_of_week) #함수가 실행된 시점에서 월요일의 날짜를 가져온다 #현재 날짜에서 현재 날짜의 값(weekday 반환 값)을 빼서 월요일의 날짜로 만듦

    for i in range(0, 8):
        erum_url = 'http://www.andong.ac.kr/main/module/foodMenu/view.do?manage_idx=73&memo5=' #채움관 식단 정보가 있는 url(날짜 빠짐)
        exact_day = standard_day + dt.timedelta(days=i)
        nowDate = str(exact_day.strftime('%Y-%m-%d'))
        erum_url = erum_url + nowDate

        req = requests.get(erum_url)
        html = req.text
        soup = BeautifulSoup(html, 'lxml')

        soup = str(soup)

        if '정보가 없습니다' in soup:
            soup = BeautifulSoup(html, 'lxml')
            check_chaeum = soup.find_all('dt')
            menu_text = str(check_chaeum[0]).replace('<dt style="width:100%; text-align:center;">', "").replace("</dt>", "").split("<br/>")
            menu_text = nowDate + ' ' + day_db_menu[i] + '\n' + str(menu_text[0]) + '\n' + str(menu_text[1])
            db_upload('이룸관', menu_text, day_db_sql[i], False, False, False)
        else:
            soup = BeautifulSoup(html, 'lxml')
            check_chaeum = soup.find_all('dd')

            breakfast = str(check_chaeum[0]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>") #Web에서 &기호 읽어들일때 amp; 라는 문장이 추가되어 제거하는 과정 추가
            lunch = str(check_chaeum[1]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>")
            dinner = str(check_chaeum[2]).replace("<dd>", "").replace("</dd>", "").replace("amp;", "").split("<br/>")

            em, el, ed = exist_check(len(breakfast), len(lunch), len(dinner))

            breakfast, lunch, dinner = menu_sum(breakfast, lunch, dinner)

            menu_text = nowDate + ' ' + day_db_menu[i] + '\n<----------조식---------->\n' + breakfast + \
                   '<----------중식---------->\n식사시간 11:50~13:30\n' + lunch + \
                   '<----------석식---------->\n식사시간 16:50~18:30\n' + dinner

            db_upload('이룸관', menu_text, day_db_sql[i], em, el, ed)

def menu_print(place, day, star_plus=0):
    day_db_h = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일', '월요일(다음주)']  # DB 텍스트에 넣을 요일 문자 리스트

    try:
        conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    except:
        print("menu_print Error")
        return 0

    cur = conn.cursor()
    sql_str = "select menu, breakfast, lunch, dinner from school_menu where place='%s' and day='%s';"%(place, day_db_h[day])

    cur.execute(sql_str)

    result = cur.fetchall()

    data = result[0][0]

    if star_plus == 1:
        breakfast_star, breakfast_cnt, lunch_star, lunch_cnt, dinner_star, dinner_cnt = star_cnt(place)

        if result[0][1] == True:  # 식단이 존재하면 별점 정보 표시
            data += "\n조식 %s %d명이 참여" % (breakfast_star, breakfast_cnt)

        if result[0][2] == True:
            data += "\n중식 %s %d명이 참여" % (lunch_star, lunch_cnt)

        if result[0][3] == True:
            data += "\n석식 %s %d명이 참여" % (dinner_star, dinner_cnt)

    return data

def restaurant_list(message):
    conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    cur = conn.cursor()
    if message == '리스트':
        sql_str = "select distinct name, tel, delivery from restaurant order by name asc;"
        cur.execute(sql_str)

        results = cur.fetchall()

        list_data = '식당 이름 / 전화번호 / 배달여부\n'
        for result in results:
            list_data += str(result[0]) + ' / ' + str(result[1]) + ' / ' + str(result[2]) + '\n'

        return list_data

    elif message == '처음으로':
        return '처음으로 돌아갑니다'

    else:
        sql_str = "select menu, price, tel, delivery from restaurant where name='%s';"%message
        cur.execute(sql_str)

        results = cur.fetchall()

        if len(results) < 2:
            return '등록된 정보가 없거나 잘못된 값을 입력했습니다.\n식당 이름은 \n리스트\n를 입력하여 참고하세요'
        else:
            tel = results[0][2]
            delivery = results[0][3]
            list_data = '%s 정보\n전화번호 : %s\n배달여부 : %s\n\n'%(message, tel, delivery)
            list_data += '메뉴 / 가격\n'
            for result in results:
                list_data += str(result[0]) + ' / ' + str(result[1]) + '\n'

            return list_data

def domitori(): #기숙사 당일 정보
    day_of_week = dt.datetime.today().weekday()

    data = menu_print('기숙사', day_of_week, 1)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return data

def domitori_tomorrow(): #기숙사 익일 정보
    day_of_week = dt.datetime.today().weekday()
    day_of_week += 1

    data = menu_print('기숙사', day_of_week)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return data

def cheaum():#채움관 당일 정보
    day_of_week = dt.datetime.today().weekday()

    data = menu_print('채움관', day_of_week, 1)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---"%random_ad()

    return data

def cheaum_tomorrow(): #채움관 익일 정보
    day_of_week = dt.datetime.today().weekday()
    day_of_week += 1

    data = menu_print('채움관', day_of_week)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return data

def erum():#이움관 당일 정보
    day_of_week = dt.datetime.today().weekday()

    data = menu_print('이룸관', day_of_week, 1)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return data

def erum_tomorrow(): #이움관 익일 정보
    day_of_week = dt.datetime.today().weekday()
    day_of_week += 1

    data = menu_print('이룸관', day_of_week)

    data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return data

def restaurant(): #양식당 정보
    res_list = ['등심돈가스: 3800원', '치즈돈가스: 4000원', '치킨까스: 3800원', '불닭덮밥: 3800원', '스팸덮밥: 3800원', '참치마요: 3500원', '김밥: 1500원', '참치김밥: 2500원', \
                '돼지등뼈곰탕: 3800원', '우동: 2500원', '샐러드파스타: 3800원', '돼지불고기덮밥: 4000원', '오리불고기덮밥: 5000원']
    rest_data = "운영시간 10:00 ~ 19:00\n(주말, 공휴일 제외)\n\n"

    for i in res_list:
        rest_data += '%s\n'%i

    rest_data += "\n\n아니면 여기는 어떨까요?\n---%s---" % random_ad()

    return rest_data

def moms(moms_type): #맘스터치 정보
    moms_data = moms_db(moms_type)

    return moms_data

def random_ad():
    rd_num = random.randint(0, 42)

    conn = psycopg2.connect("dbname=k_userkey user=postgres host=localhost password=474849")
    cur = conn.cursor()
    sql_str = "select distinct name from restaurant order by name asc limit 1 offset %d;"%rd_num
    cur.execute(sql_str)

    results = cur.fetchall()
    results = results[0]

    return results

if __name__ == "__main__":
    day_of_week = dt.datetime.today().weekday()
    if day_of_week == 0:
        school_menu_delete()
        domitori_create()
        cheaum_create()
        erum_create()
    else:
        pass
    star_reset()