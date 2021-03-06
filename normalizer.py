import regex as re


class Normalizer:
    '''
    Проблема алгоритма в неотличимости имени от фамилии
    (если вдруг будет подаваться формат ИО или ИФО и т.д.)
    '''

    def __init__(self, headers: list):
        self.headers = {key: value for value, key in enumerate(headers)}
        self.surname_pattern = re.compile(r".{3}((вич)|(вна))$", re.IGNORECASE)
        self.phone_pattern = {
            'main': re.compile(r"[\s+]*(7|8)*"      #1
                               r"[\s\-\(]*(\d{3})"  #2
                               r"[\s\-\)]*(\d{3})"  #3
                               r"[\s\-]*(\d{2})"    #4
                               r"[\s\-]*(\d{2}).*"),#5
            "additional": re.compile(r"[\s\S]*(\d{4})")
        }

    @property
    def __len_headers(self):
        return len(self.headers)

    def __is_surname(self, name: str):
        return self.surname_pattern.search(name) is not None

    def __extract_full_name(self, raw_row: list) -> list:
        return [raw_row[self.headers['lastname']], raw_row[self.headers['firstname']], raw_row[self.headers['surname']]]

    def __name_normalize(self, raw_row: list) -> list:
        return " ".join(self.__extract_full_name(raw_row)).strip().split()

    def __phone_normalize(self, phone: str) -> str:
        numbers = phone.split('доб.')
        phone_number = self.phone_pattern['main'].sub(fr'+7(\2)\3-\4-\5', numbers[0])

        if len(numbers) > 1:
            additional_part = self.phone_pattern['additional'].match(numbers[1]).groups()
            phone_number = f'{phone_number} доб.{additional_part[0]}'

        return phone_number

    def __strip_row(self, raw_row: list) -> list:
        return raw_row[:self.__len_headers]

    def row_normalize(self, raw_row: list) -> list:
        '''pure function'''

        row_normalize = self.__strip_row(raw_row)
        normal_name = self.__name_normalize(raw_row)

        if self.__is_surname(normal_name[-1]):
            row_normalize[self.headers['surname']] = normal_name[-1]
            normal_name = normal_name[0: -1]

        for i, part_name in enumerate(normal_name):
            row_normalize[i] = part_name

        phone = row_normalize[self.headers['phone']]
        if phone != '':
            row_normalize[self.headers['phone']] = self.__phone_normalize(phone)

        return row_normalize

    def merge_not_unique(self, contacts_list: list) -> list:
        """pure function"""
        unique_list = [contacts_list[0]]

        for idx, item in enumerate(contacts_list[1:]):
            for unique_idx, unique_item in enumerate(unique_list):
                if self.__is_merges_rows(item, unique_item):
                    unique_list[unique_idx] = self.__merge_rows(unique_item, item)
                    break
            else:
                unique_list.append(item)

        return unique_list

    def __merge_rows(self, first: list, second: list) -> list:
        result = first[:]
        for i in range(self.__len_headers):
            if second[i] != '':
                result[i] = second[i]
        return result

    def __is_one_human(self, first_human_name: list, second_human_name: list):
        full_name = set(self.__extract_full_name(first_human_name) + self.__extract_full_name(second_human_name))
        full_name = " ".join(full_name).strip().split(" ")
        if len(full_name) > 3:
            return False
        return True

    def __is_merges_rows(self, first: list, second: list):
        if first == second:
            return False

        if not self.__is_one_human(first, second):
            return False

        for item1, item2 in zip(first, second):
            if not (item1 == '' or item2 == '' or item2 == item1):
                return False
        return True
