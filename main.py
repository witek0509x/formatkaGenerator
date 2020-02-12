import requests
import time

def convert_dates(date):
    date = date[:-1].split("T")
    date[0] = date[0].split("-")
    date[1] = date[1].split(":")
    return date[0] + date[1]


def compare_dates(date_to_compare, date_to_be_compared):
    date_to_compare = convert_dates(date_to_compare)
    date_to_be_compared = convert_dates(date_to_be_compared)
    for i in range(len(date_to_compare)):
        if date_to_compare < date_to_be_compared:
            return -1
        if date_to_compare > date_to_be_compared:
            return 1
    return 0


def binary_search(token, date, up_bound, down_bound, all):
    current = int((up_bound - down_bound) / 2) + down_bound
    response = requests.get(
        "https://gis-api.aiesec.org/v2/people?access_token=" + token +
        "&page=" + str(current) + "&per_page=25&filters[home_committee]=1483&"
        "api_key=" + token)
    print("target:", date, "actual:", response.json()["data"][24]["created_at"])
    if compare_dates(date, response.json()["data"][24]["created_at"]) == -1:
        return binary_search(token, date, up_bound, current, all)
    elif compare_dates(date, response.json()["data"][0]["created_at"]) == 1:
        return binary_search(token, date, current, down_bound, all)
    else:
        return current


with open("token.txt", "r") as file:
    token = file.readline()
    token = token[:-1]

with open("last_date.txt", "r") as file1:
    previous_date = file1.readline().replace("\n", "")
if previous_date == "":
    previous_date = "0000-00-00T00:00:00Z"
print(previous_date)

start_time = time.time()
response = requests.get(
    "https://gis-api.aiesec.org/v2/people?access_token=" + token +
    "&page=1&per_page=25&filters[home_committee]=1483&"
    "api_key=" + token)
total_size = response.json()["paging"]["total_items"]
foo = total_size % 25 == 0
if foo : foo = 0
else : foo = 1
final_page = binary_search(token, previous_date, int(total_size/25) + foo, 1, int(total_size/25) + foo)
print("end point found")
print(time.time() - start_time)
for page in range(final_page):
    response = requests.get(
        "https://gis-api.aiesec.org/v2/people?access_token=" + token +
        "&page=" + str(page+1) + "&per_page=25&filters[home_committee]=1483&"
        "api_key=" + token)
    with open("result.csv", "a") as file:
        last_date = ""
        for person in response.json()["data"]:
            should_be_checked = False
            for manager in person["managers"]:
                if manager["full_name"] == "DIMA RASHIDOV":
                    should_be_checked = True
            if compare_dates(previous_date, person["created_at"]) > -1: should_be_checked = False
            if should_be_checked:
                person_string = ",".join([str(person["full_name"]), str(person["id"]), str(person["phone"]),
                                          str(person["email"]), str(person["created_at"].split("T")[0])]) + "\n"
                try:
                    file.write(person_string)
                except:
                    print("failed to save person " + person["full_name"] + "of id " + str(person["id"]) + "on page " + str(page+1))

    print(((page+1)/final_page)*100, "%")


response = requests.get(
    "https://gis-api.aiesec.org/v2/people?access_token=" + token +
    "&page=1&per_page=1&filters[home_committee]=1483&"
    "api_key=" + token)
last_date = response.json()["data"][0]["created_at"]
with open("last_date.txt", "w") as file:
    file.write(last_date)


