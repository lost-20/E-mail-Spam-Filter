import re
import base64
import email

number_of_test = 15
spam_score = 0
#str = bytes.fromhex('D097D0B4')
#print(bytes.decode(str, encoding='utf-8'))


def image(text):  # проверяет загаловоки Content-Type, если его тип только image, значит в теле письма только изображение
    im = r"Content-Type: image/.+"
    count = re.findall(im, text)
    return count


def tags(text):  # подсчитывает количество логических тегов в тексте
    tag = r"<a>|<em>|<strong>|<small>|<s>|<cite>|<q>|<dfn>|<abbr>|<ruby>|<rb>|<rp>|<rt>|<rtc>|<data>|<time>|<code>|<var>|<samp>|<kbd>|<sub>|<sup>|<i>|<b>|<u>|<mark>|<bdi>|<bdo>|<span>|<br>|<wbr>|<h1>|<h2>|<h3>|<h4>|<h5>|<h6>"
    count = re.findall(tag, text)
    return count


def density(text):  # подсчитывает плотность вхождения всех слов
    word = r"\b\w*.?\b"  # учитывает слова любой длины
    #word = r"\b\w{2,}\b"  # учитывает слова длины больше 2
    words = re.findall(word, text)
    count = [['', 0]]
    i = 0
    for wrd in words:
        for i in range(len(count)):
            if count[i][0] == wrd:
                count[i][1] += 1
                break
            if i == len(count) - 1:
                count.append([wrd, 1])
    count = count[1:]
    number_of_words_in_text = len(count)
    for wrd in count:
        wrd[1] = wrd[1] / number_of_words_in_text * 100
    return count


def text_decoding(text, B64):  # декодирует текст
    try:
        return base64.b64decode(text).decode()
    except ValueError:
        text += '.'
        text = text.replace('&nbsp', ' ')
        text = text.replace('&ldquo', "'")
        text = text.replace('&rdquo', "'")
        text = text.replace('_', " ")
        bytes_in_string = re.findall(r"(=\w\w| |,|\.|-|!|['])", text)  # регулярное выражения для нахождения байтов в тексте
        empty = True
        for byte in bytes_in_string:
            if len(byte) == 3:
                empty = False
                break
        if empty:
            return text[:-1]
        decoded_text = ""
        tmp = ""
        # раскодирование байтов
        for i in range(len(bytes_in_string)):
            if len(bytes_in_string[i]) == 3:
                tmp += str(bytes_in_string[i])[1:]
            else:
                try:
                    raw_byte = bytes.fromhex(tmp)
                except ValueError:
                    return
                try:
                    decoded_text += bytes.decode(raw_byte, encoding='utf-8')
                    tmp = ""
                    decoded_text += bytes_in_string[i]
                except ValueError:
                    return ""
        if not decoded_text:
            return text[:-1]
        else:
            return decoded_text[:-1]


def spam_in_text(text, email):
    global spam_score
    decoded_text = text_decoding(text, False)
    if decoded_text == '\n':
        if not text:
            #print("В письме отсутствует текст.")
            return
        #print()
        spam_image = image(email)
        if spam_image:
            spam_image = True
        else:
            spam_image = False
        if (spam_image) & (decoded_text == '\n'):
            print("3) В теле письма только картинка. Возможен спам.")
            spam_score += 1
            print()
            return
    #print("Текст в письме: ")
    #print(decoded_text)
    #print()
    count = density(decoded_text)
    spam_density = False
    #print("1) Плотность вхождения:")
    for word in count:
        if word[1] > 5:
            print("1) Плотность вхождения слова " + word[0] + " - " + str(word[1]) + "%")
            spam_density = True
    if spam_density:
        print("Возможен спам.")
        spam_score += 1
        print()
    #else:
        #print("1) Вхождение каждого слова не превышает 5%.")
        #print()
    tag = tags(email)
    #print("2) Обнаружены теги: " + " ".join(tag))
    spam_image = image(email)
    #if spam_image:
        #print("3) В теле письма находятся картинка и текст.")
        #print()
    #else:
        #print("3) В теле письма нет картинки.")
        #print()
    if len(tag) == 0:
        return
    if len(tag) > 8:
        print("2) Количество логических тегов равно " + str(len(tag)) + ". Возможен спам.")
        print("2) Обнаружены теги: " + " ".join(tag))
        spam_score +=1
        print()
    else:
        print("2) Количество логических тегов равно " + str(len(tag)) + ".")
        print("2) Обнаружены теги: " + " ".join(tag))
        print()
    return


def spam_subject(text, email):  # декодирует поле Subject и смотрит на совпадения с текстом
    global spam_score
    try:
        decoded_text = text_decoding(text, False)
    except ValueError:
        decoded_text = ""
    subject_regex_base64 = r"Subject:.+\?B\?.+|Subject:.+\?b\?.+"
    subject_regex = r'Subject:.+\?Q\?.+|Subject:.+\?q\?.+'
    subject_regex_decoded = r'Subject:.+'
    subject = re.findall(subject_regex, email)
    subject_base64 = re.findall(subject_regex_base64, email)
    subject_decoded = re.findall(subject_regex_decoded, email)
    B64 = False
    if not subject:
        if not subject_base64:
            if not subject_decoded:
                #print("4) Тема в письме отсутствует.")
                print()
                return
    if subject_base64:
        B64 = True
        subject = subject_base64
    if (not subject_base64) & (not subject):
        while len(subject_decoded) > 1:
            subject_decoded.pop(0)
        bytes = subject_decoded[0][8:]
        decoded_subject = bytes
    else:
        while len(subject) > 1:
            subject.pop(0)
        bytes = subject[0][19:-2]
        try:
            decoded_subject = text_decoding(bytes, B64)
        except ValueError:
            decoded_text = ""
    #print("4) Тема письма:")
    #print()
    #print(decoded_subject)
    #print()
    if not decoded_subject:  # если нет темы или письма, то возможно это спам
        return False
    if not decoded_text:
        return False
    decoded_text = decoded_text.split(" ")
    decoded_subject = decoded_subject.split(" ")
    matches = []
    for word in decoded_subject:
        for wrd in decoded_text:
            if word == wrd:
                matches.append(wrd)
    if matches:  # если больше 2х совпадений, то это не спам
        return matches
    else:
        return False


def title_header(email):
    global spam_score
    try:
        text_start_index = email.index("<title>")
    except ValueError:
        #print("5) Title отсутствует в письме.")
        #print()
        return
    if email[text_start_index + 7] == '<':
        #print("5) Title пустой.")
        #print()
        return
    title = ""
    while True:
        if email[text_start_index] == '<':
            if email[text_start_index + 1] == '/':
                if email[text_start_index + 2] == 't':
                    if email[text_start_index + 3] == 'i':
                        break
        title += email[text_start_index]
        text_start_index += 1
    try:
        decoded_title = text_decoding(title, False)
    except ValueError:
        decoded_title = title
    char_counter = 0
    for char in decoded_title: char_counter += 1
    spam = False
    if char_counter > 119:
        print("5) Title документа длиннее 120 символов (" + str(char_counter) + " символов). Возможен спам.")
        print()
        spam = True
    word = r"\b\w*.?\b"
    word_counter = re.findall(word, decoded_title)
    if len(word_counter) > 12:
        print("5) Title документа длиннее 12 слов (" + str(len(word_counter)) + " слов). Возможен спам.")
        print()
        spam = True
    if spam:
        spam_score += 1
    #if not spam:
        #print("5) Title документа не превышает 12 слов или 120 символов.")
        #print()


def description_header(email):  # смотрит сколько слов и символоа в meta name description
    global spam_score
    try:
        text_start_index = email.index('<meta name="description"')
    except ValueError:
        #print("6) Meta name 'description' отсутствует в письме.")
        #print()
        return
    text_start_index += 34
    description = ""
    while True:
        if email[text_start_index] == '"':
            break
        description += email[text_start_index]
        text_start_index += 1
    char_counter = 0
    for char in description: char_counter += 1
    spam = False
    if char_counter > 250:
        print("6) Meta name 'description' длиннее 250 символов (" + str(char_counter) + " символов). Возможен спам.")
        print()
        spam = True
    word = r"\b\w*.?\b"
    word_counter = re.findall(word, description)
    if len(word_counter) > 40:
        print("6) Meta name 'description' длиннее 40 слов (" + str(len(word_counter)) + " слов). Возможен спам.")
        print()
        spam = True
    if spam:
        spam_score += 1
    #if not spam:
        #print("6) Meta name 'description' не превышает 40 слов или 250 символов.")
        #print()
    return


def keywords_header(email):  # смотрит сколько слов и символоа в meta name keywords
    global spam_score
    try:
        text_start_index = email.index('<meta name="keywords"')
    except ValueError:
        #print("7) Meta name 'keywords' отсутствует в письме.")
        #print()
        return
    text_start_index += 31
    keywords = ""
    while True:
        if email[text_start_index] == '"':
            break
        keywords += email[text_start_index]
        text_start_index += 1
    char_counter = 0
    for char in keywords: char_counter += 1
    spam = False
    if char_counter > 250:
        print("7) Meta name 'keywords' длиннее 250 символов (" + str(char_counter) + " символов). Возможен спам.")
        print()
        spam = True
    word = r"\b\w*.?\b"
    word_counter = re.findall(word, keywords)
    if len(word_counter) > 40:
        print("7) Meta name 'keywords' длиннее 40 слов (" + str(len(word_counter)) + " слов). Возможен спам.")
        print()
        spam = True
    if spam:
        spam_score += 1
    #if not spam:
        #print("7) Meta name 'keywords' не превышает 40 слов или 250 символов.")
        #print()
    return


def apparently_to(email, email_for_lines):  # Проверяет число получаиелей в Apparently-To
    global spam_score
    try:
        text_start_index = email.index('X-Apparently-To:')
    except ValueError:
        #print("8) Заголовок X-Apparently-To: отсутствует в письме.")
        #print()
        lines = email_for_lines
        return lines
    lines = email_for_lines
    regex_apparently = r'X-Apparently-To:'
    apparently = []
    for i in range(len(lines) - 1):
        match = re.findall(regex_apparently, lines[i])
        if match:
            apparently.append(lines[i])
            i += 1
            while lines[i][0] == ' ':
                apparently.append(lines[i])
                i += 1
            break
    email_regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    emails = set()
    for email in apparently:
        match = re.search(email_regex, email)
        if match:
            emails.add(match.group(0))
    if len(emails) > 5:
        print("8) В заголовке Apparantly-To большое число получателей = " + str(len(emails)) + ". Возможен спам.")
        spam_score += 1
        print()
        for email in emails:
            print(email)
        print()
    #else:
        #print("8) В заголовке Apparently-To небольшое число получателей = " + str(len(emails)) + ".")
        #print()
        #for email in emails:
            #print(email)
        #print()
    return lines


def cc_header(email, lines):  # Проверяет число получателей в Cc
    global spam_score
    try:
        cc = email.index("Cc:")
    except ValueError:
        return
    cc = []
    regex_to = r'^Cc:'
    for i in range(len(lines) - 1):
        match = re.findall(regex_to, lines[i])
        if match:
            cc.append(lines[i])
            i += 1
            while lines[i][0] == ' ':
                cc.append(lines[i])
                i += 1
            break
    email_regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    emails = set()
    for email in cc:
        match = re.search(email_regex, email)
        if match:
            emails.add(match.group(0))
    if len(emails) > 4:
        print("8) В заголовке CC указано большое число получаетелей = " + str(len(emails)) + ". Возможно спам.")
        spam_score += 1
        print()
        for email in emails:
            print(email)
        print()
    #else:
        #print("8) В заголовке CC указано небольшое число получателей = " + str(len(emails)) + ".")
        #print()
        #for email in emails:
            #print(email)
        #print()
    return


def to_header(lines):  # Проверяет число получателей в TO
    global spam_score
    to = []
    regex_to = r'^To:'
    for i in range(len(lines) - 1):
        match = re.findall(regex_to, lines[i])
        if match:
            to.append(lines[i])
            i += 1
            while lines[i][0] == ' ':
                to.append(lines[i])
                i += 1
            break
    email_regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    emails = set()
    for email in to:
        match = re.search(email_regex, email)
        if match:
            emails.add(match.group(0))
    if len(emails) == 0:
        #print("8) Заголовок To отсутствует.")
        #print()
        return
    if len(emails) > 4:
        print("8) В заголовке To указано большое число получаетелей = " + str(len(emails)) + ". Возможно спам.")
        spam_score += 1
        print()
        for email in emails:
            print(email)
        print()
    #else:
        #print("8) В заголовке To указано небольшое число получателей = " + str(len(emails)) + ".")
        #print()
        #for email in emails:
            #print(email)
        #print()
    return


def return_path_header(lines):  # Проверяет обратный адрес в Return-Path
    regex = r"^Return-Path:"
    path = []
    for i in range(len(lines) - 1):
        match = re.findall(regex, lines[i])
        if match:
            path.append(lines[i])
            i += 1
            while lines[i][0] == ' ':
                path.append(lines[i])
                i += 1
            break
    if not path:
        #print("9) Заголовок Return-Path отсутствует.")
        #print()
        return
    email_regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    email_regex2 = r'[<][a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}[>]'
    emails = set()
    for email in path:
        match = re.findall(email_regex, email)
        match2 = re.findall(email_regex2, email)
        if match:
            emails.add("".join(match))
        if match2:
            emails.add("".join(match2))
    if emails:
        #print("9) В заголовке Return-Path указан обратный адрес.")
        #print()
        #for email in emails:
            #print(email)
        #print()
        return True
    else:
        print("9) Указан некорректный адрес электронной почты в заголовке Return-Path. Возможно спам.")
        print()
        return


def from_header(lines):  # Проверяет обратный адрес в From
    regex = r"^From:"
    From = []
    for i in range(len(lines) - 1):
        match = re.findall(regex, lines[i])
        if match:
            From.append(lines[i])
            i += 1
            while lines[i][0] == ' ':
                From.append(lines[i])
                i += 1
            break
    if not From:
        #print("9) Заголовок From отсутствует.")
        #print()
        return
    email_regex = r'[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}'
    email_regex2 = r'[<][a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}[>]'
    emails = set()
    for email in From:
        match = re.fullmatch(email_regex, email)
        match2 = re.findall(email_regex2, email)
        if match:
            emails.add(match.group(0))
        if match2:
            emails.add("".join(match2))
    if emails:
        #print("9) В заголовке From указан обратный адрес.")
        #print()
        #for email in emails:
            #print(email)
        #print()
        return True
    else:
        print("9) Указан некорректный адрес электронной почты в заголовке From. Возможно спам.")
        print()
        return


def bcc_header(email):  # Проверяет наличие BCC
    global spam_score
    try:
        bcc = email.index("BCC: ")
    except ValueError:
        #print("10) Заголовок BCC отсутствует.")
        #print()
        return
    print("10) Присутствует заголовок BCC. Возможно спам.")
    spam_score += 1
    print()
    return


def comments_header(email):  # Проверяет наличие Comments
    global spam_score
    try:
        commnents = email.index("Comments: ")
    except ValueError:
        #print("11) Заголовок Comments отсутствует.")
        #print()
        return
    print("11) Присутствует заголовок Comments. Возможно спам.")
    spam_score += 1
    print()
    return


def message_id(lines):  # Проверяет корректность идентификатора в Message-ID
    global spam_score
    message_regex = r"^(Message-ID:.+)|(Message-Id:.+)"
    message = []
    for line in lines:
        if re.findall(message_regex, line):
            message.append(line)
            break
    if not message:
        #print("12) Заголовок Message-ID не обнаружен.")
        #print()
        return
    email = message[0][13:-2]
    blank = False
    dog = True
    for char in email:
        if char == " ":
            blank = True
        if char == "@":
            dog = False
    if dog | blank:
        print("12) В заголовке Message-ID структура идентификатора нарушена. Возможен спам.")
        print(email)
        spam_score += 1
        print()
        return
    #print("12) Структура идентификатора Message-ID не нарушена.")
    #print()
    #print()


def in_reply_to(email):  # Проверяет наличие In-Reply-To
    global spam_score
    try:
        reply = email.index("In-Reply-To")
    except ValueError:
        #print("13) Заголовок In-Reply-To не обнаружен.")
        #print()
        return
    print("13) Замечен заголовок In-Reply-To. Возможно спам.")
    print()
    spam_score += 1


def priority(email):  # Проверяет поле в Priority
    global spam_score
    try:
        urgent = email.index("Priority: urgent")
    except ValueError:
        #print("14) В заголовке Priority не обнаружено поле urgent.")
        #print()
        return
    print("14) В заголовке Priority указано поле urgent. Возможно спам.")
    print()
    spam_score += 1


def uidl_header(email):
    global spam_score
    try:
        uidl = email.index("X-UIDL")
    except ValueError:
        #print("15) Заголовок X-UIDL не обнаружен.")
        #print()
        return
    print("15) Обнаружен заголовок X-UIDL. Возможно спам.")
    print()
    spam_score += 1


def spam_in_headers(text, email, email_for_lines):
    global spam_score
    subject = spam_subject(text, email)
    if not subject:
        print("4) Совпадений в теме письма и в его тексте не обнаружено. Возможно спам.")
        print()
        spam_score += 1
    #else:
        #print("4) Совпадения в теме письма и в его тексте присутствуют.")
        #for word in subject: print(word)
        #print()
    title_header(email)
    description_header(email)
    keywords_header(email)
    lines = apparently_to(email, email_for_lines)
    to_header(lines)
    cc_header(email, lines)
    spam_path = False
    spam_from = False
    if not return_path_header(lines):
        spam_path = True
    if not from_header(lines):
        spam_from = True
    if spam_from and spam_path:
        print("9) Отсутсвует обратный адрес. Возможно спам.")
        spam_score += 1
        print()
    bcc_header(email)
    comments_header(email)
    message_id(lines)
    in_reply_to(email)
    priority(email)
    uidl_header(email)
    return


def main():
    global spam_score
    global number_of_test
    print("Введите название файла:")
    file = input()
    email_for_lines = open(file, 'r').readlines()
    email = open(file, 'r').read()
    # Нахождение текста в письме
    try:
        text_start_index = r"Content-Type: text/plain; charset=|Content-Type: Text/plain; charset=|Content-Type: Text/Plain; charset="
        tmp = text_start_index
        text = []
        for i in range(len(email_for_lines) - 1):
            match = re.findall(text_start_index, email_for_lines[i])
            if match:
                while email_for_lines[i][0] != '\n':
                    i += 1
                i += 1
                while (email_for_lines[i][0] != '-') & (i < len(email_for_lines) -1):
                    text.append(email_for_lines[i])
                    i += 1
                break
        text = "".join(text)
        if text == "":
            try:
                email = base64.b64decode(email).decode()
                email_for_lines = email.split("\n")
                text_start_index = r"Content-Type: text/plain; charset=|Content-Type: Text/plain; charset=|Content-Type: Text/Plain; charset="
                tmp = text_start_index
                text = []
                for i in range(len(email_for_lines) - 1):
                    match = re.findall(text_start_index, email_for_lines[i])
                    if match:
                        while email_for_lines[i][0] != '\n':
                            i += 1
                        i += 1
                        while (email_for_lines[i][0] != '-') & (i < len(email_for_lines) - 1):
                            text.append(email_for_lines[i])
                            i += 1
                        break
            except ValueError:
                print()
        text = "".join(text)
        spam_in_text(text, email)
        spam_in_headers(text, email, email_for_lines)
        print("Вывод: Всего проведено тестов - " + str(number_of_test) + ".")
        print("Количество совпавших признаков: " + str(spam_score) + ".")
        if spam_score == 0:
            print("Вероятность спама - 0%.")
        else:
            print("Вероятность спама - " + str(spam_score / number_of_test * 100) + "%.")
        print("Нажмите любую кнопку для завершения.")
        input()
        return
    except ValueError:
        spam_in_headers("", email, email_for_lines)
        print("Вывод: Всего проведено тестов - " + str(number_of_test - 3) + ".")
        print("Количество совпавших признаков: " + str(spam_score) + ".")
        if spam_score == 0:
            print("Вероятность спама - 0%.")
        else:
            print("Вероятность спама - " + str((spam_score) / (number_of_test - 3) * 100) + "%.")
        print("Нажмите любую кнопку для завершения.")
        input()
        return


if __name__ == "__main__":
    main()