from normalizer import Normalizer
import csv


if __name__ == "__main__":
    with open("phone_raw.csv", encoding='utf-8') as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)

    normalizer = Normalizer(contacts_list[0])
    for idx, item in enumerate(contacts_list[1:]):
        contacts_list[idx+1] = normalizer.row_normalize(item)

    unique_list = normalizer.merge_not_unique(contacts_list)

    with open("phonebook.csv", "w", encoding='utf-8') as f:
        datawriter = csv.writer(f, delimiter=',')
        # Вместо contacts_list подставьте свой список
        datawriter.writerows(unique_list)
