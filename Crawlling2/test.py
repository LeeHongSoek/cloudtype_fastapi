# 빈 리스트 생성
my_list = []

# 리스트에 요소 추가
my_list.append(1)
my_list.append(2)
my_list.append(3)

print(my_list)  # [1, 2, 3] 출력

# 리스트 요소 접근
print(my_list[0])  # 1 출력
print(my_list[1])  # 2 출력

# 리스트 요소 변경
my_list[2] = 4
print(my_list)  # [1, 2, 4] 출력

# 리스트 길이 확인
print(len(my_list))  # 3 출력

# 반복문을 통한 리스트 순회
for element in my_list:
    print(element)

# 리스트 요소 추가
my_list.append(5)
print(my_list)  # [1, 2, 4, 5] 출력

# 리스트 요소 삭제
del my_list[1]


print(my_list)  # [1, 4, 5] 출력
