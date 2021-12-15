# E-mail-Spam-Filter
Программа выполнена на языке python3.
Исходный код программы находится в файле main.py.
Все функции в файле main.py прокомментированы. 
Для запуска программы необходимо запустить файл main.exe.
После запуска программы необходимо ввести имя файла (электронного письма) вместе с расширением.
Все эти письма хранятся в том же каталоге, что и исполняющий файл.
Описание файлов:
1) sраm3.txt - Признаки спама.
2) image.mbox - Использовался для тестирования признака - "в теле письма только картинка".
3) image_with_text.mbox - Письмо с картинкой и текстом в теле письма.
4) image_with_re - Письмо только с картинкой и темой.
5) subject.mbox - Использовался для тестирования признака - "совпадение в теме и в теле письма".
6) document.mbox - Использовался для тестирования заголовка title, а также meta name "description"/keywords.
7) cc.mbox - Использовался для тестирования получателя копии письма.
8) apparently-to.mbox - Использовался для тестирования заголовка "Apparently-To", а также содержит относительно большое число получателей.
В качестве вывода программа выводит все найденные признаки спама, и подсчитывает количество совпавших признаков.
