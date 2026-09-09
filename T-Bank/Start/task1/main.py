s = input()
n = len(s)
arr = []
for i in range(n):
    arr.append(s[i])

for i in range(n-1):
    for j in range(i+1, n):
        if arr[i] > arr[j]:
            temp = arr[i]
            arr[i] = arr[j]
            arr[j] = temp

if arr[0] == '0':
    for i in range(1, n):
        if arr[i] != '0':
            temp = arr[0]
            arr[0] = arr[i]
            arr[i] = temp
            break

result = ''
for i in range(n):
    result += arr[i]
    
print(result)