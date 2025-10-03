from collections import defaultdict
class Solution:
    def findHighAccessEmployees(self, access_times: List[List[str]]) -> List[str]:
        employee_access = defaultdict(list)
        for emp, time in access_times:
            hours = int(time[:2])
            minutes = int(time[2:])
            total_minutes = hours*60 + minutes
            employee_access[emp].append(total_minutes)
        
        high_access_employees = []

        for emp, access_time_list in employee_access.items():
            access_time_list.sort()

            for i in range(2, len(access_time_list)):
                if access_time_list[i] - access_time_list[i-2] < 60 :
                    high_access_employees.append(emp)
                    break

        return high_access_employees

"""    
time and space 

n = total no of entries, m = no of distinct emp, ki = no of entreis for ith emp

o(n) + o(m*(n/m*logn + n/m)) = o(nlogn)

o(n)
"""