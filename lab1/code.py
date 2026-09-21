EPS = 1e-9



# ДАННЫЕ ЗАДАЧИ
# менять в основном только это

# Z = 4x1 + x2 + x3 + 2x4 -> min
c = [4, 1, 1, 2]

# коэффициенты ограничений
A = [
    [2, 1, 0, 1],
    [1, 1, 1, 0],
    [0, 0, 1, 1]
]

# знаки ограничений
signs = ["<=", "=", ">="]

# правые части
b = [9, 7, 5]

# min или max
task_type = "min"


# добавляет новый столбец в матрицу
def add_column(A, values):
    for i in range(len(A)):
        A[i].append(float(values[i]))


# просто печатает таблицу
def show_table(title, basis, free, A, b, p, Q):
    print("\n" + title)
    print("Базис\t" + "\t".join(free) + "\tb")

    for i in range(len(A)):
        print(basis[i], end="\t")

        for value in A[i]:
            print(round(value, 4), end="\t")

        print(round(b[i], 4))

    print("p", end="\t")

    for value in p:
        print(round(value, 4), end="\t")

    print(round(-Q, 4))


# один пересчет симплекс-таблицы
def pivot(basis, free, A, b, p, Q, enter, leave):
    a = A[leave][enter]  # разрешающий элемент

    # сохраняем старую таблицу
    old_A = [row[:] for row in A]
    old_b = b[:]
    old_p = p[:]

    rows = len(A)
    cols = len(free)

    # разрешающая строка
    for j in range(cols):
        if j == enter:
            A[leave][j] = 1 / a
        else:
            A[leave][j] = old_A[leave][j] / a

    b[leave] = old_b[leave] / a

    # остальные строки
    for i in range(rows):
        if i == leave:
            continue

        for j in range(cols):
            if j == enter:
                A[i][j] = -old_A[i][enter] / a
            else:
                A[i][j] = (
                    old_A[i][j]
                    - old_A[leave][j] * old_A[i][enter] / a
                )

        b[i] = (
            old_b[i]
            - old_b[leave] * old_A[i][enter] / a
        )

    # нижняя строка
    for j in range(cols):
        if j == enter:
            p[j] = -old_p[enter] / a
        else:
            p[j] = (
                old_p[j]
                - old_A[leave][j] * old_p[enter] / a
            )

    Q = (
        Q
        + old_p[enter] * old_b[leave] / a
    )

    # входящая идет в базис,
    # выходящая становится свободной
    basis[leave], free[enter] = free[enter], basis[leave]

    return Q


# обычный симплекс для задачи на минимум
def simplex(title, basis, free, A, b, p, Q):
    show_table(
        title + " - начальная таблица",
        basis, free, A, b, p, Q
    )

    step = 1

    while True:
        # ищем отрицательные элементы снизу
        negative = []

        for j in range(len(p)):
            if p[j] < -EPS:
                negative.append(j)

        # отрицательных нет -> минимум найден
        if len(negative) == 0:
            break

        # самый отрицательный элемент
        # задает разрешающий столбец
        enter = min(
            negative,
            key=lambda j: p[j]
        )

        # ищем разрешающую строку
        ratios = []

        for i in range(len(A)):
            # b / a считаем только если a > 0
            if A[i][enter] > EPS:
                ratios.append(
                    (
                        b[i] / A[i][enter],
                        i
                    )
                )

        # положительных коэффициентов нет
        if len(ratios) == 0:
            print("\nЦелевая функция не ограничена.")
            return None

        # берем минимальное b / a
        leave = min(
            ratios,
            key=lambda x: x[0]
        )[1]

        print("\nВходит:", free[enter])
        print("Выходит:", basis[leave])
        print(
            "Разрешающий элемент:",
            round(A[leave][enter], 4)
        )

        Q = pivot(
            basis,
            free,
            A,
            b,
            p,
            Q,
            enter,
            leave
        )

        show_table(
            title + " - таблица " + str(step),
            basis,
            free,
            A,
            b,
            p,
            Q
        )

        step += 1

    return Q


# вся задача целиком
def solve(c, A, signs, b, task_type):

    # делаем копии, чтобы исходные данные не испортить
    c = [float(x) for x in c]

    A = [
        [float(x) for x in row]
        for row in A
    ]

    b = [float(x) for x in b]
    signs = signs[:]

    # количество исходных переменных
    n = len(c)

    # количество ограничений
    m = len(A)

    # простая проверка
    if len(b) != m or len(signs) != m:
        print("Ошибка в размерах данных")
        return

    for row in A:
        if len(row) != n:
            print("Ошибка в матрице A")
            return


    # если справа b < 0

    for i in range(m):
        if b[i] < 0:

            b[i] = -b[i]

            for j in range(n):
                A[i][j] = -A[i][j]

            # знак тоже переворачивается
            if signs[i] == "<=":
                signs[i] = ">="

            elif signs[i] == ">=":
                signs[i] = "<="



    # 1. канонический вид

    names = []

    for i in range(n):
        names.append("x" + str(i + 1))

    next_x = n + 1

    for i in range(m):

        # <= : добавляем +x
        if signs[i] == "<=":

            column = [0.0] * m
            column[i] = 1.0

            add_column(A, column)

            names.append(
                "x" + str(next_x)
            )

            next_x += 1


        # >= : добавляем -x
        elif signs[i] == ">=":

            column = [0.0] * m
            column[i] = -1.0

            add_column(A, column)

            names.append(
                "x" + str(next_x)
            )

            next_x += 1


        # равенство уже подходит
        elif signs[i] == "=":
            pass

        else:
            print(
                "Неизвестный знак:",
                signs[i]
            )
            return


    print("\nКАНОНИЧЕСКИЙ ВИД")

    for i in range(m):
        print(
            [round(x, 4) for x in A[i]],
            "=",
            round(b[i], 4)
        )


    # запоминаем обычные и дополнительные переменные
    canonical_names = names[:]



    # 2. вспомогательная задача


    artificial = []

    # на каждую строку своя искусственная переменная
    for i in range(m):
        artificial.append(
            "x" + str(next_x + i)
        )

    # сначала искусственные базисные
    basis = artificial[:]

    # остальные свободные
    free = names[:]

    print("\nВСПОМОГАТЕЛЬНАЯ ЗАДАЧА")

    print(
        "W = "
        + " + ".join(artificial)
        + " -> min"
    )

    # нижняя строка вспомогательной таблицы
    # минус сумма коэффициентов столбца
    p = []

    for j in range(len(free)):

        column_sum = 0.0

        for i in range(m):
            column_sum += A[i][j]

        p.append(-column_sum)

    # свободный член
    Q = sum(b)


    # решаем вспомогательную задачу
    Q = simplex(
        "Вспомогательная задача",
        basis,
        free,
        A,
        b,
        p,
        Q
    )

    if Q is None:
        return


    # если W* не 0, допустимого решения нет
    if Q > EPS:

        print(
            "\nW* =",
            round(Q, 6)
        )

        print(
            "Допустимых решений нет."
        )

        return


    print("\nW* = 0")
    print("Можно переходить к основной задаче.")

    print(
        "Базис после вспомогательной задачи:",
        basis
    )


    # =========================
    # 3. если искусственная переменная
    # осталась в базисе с нулем,
    # пробуем заменить ее обычной
    # =========================

    row = 0

    while row < len(basis):

        if basis[row] in artificial:

            enter = None

            # ищем обычную переменную,
            # которую можно поставить в базис
            for j in range(len(free)):

                if (
                    free[j] not in artificial
                    and abs(A[row][j]) > EPS
                ):
                    enter = j
                    break


            if enter is not None:

                dummy_p = [0.0] * len(free)

                pivot(
                    basis,
                    free,
                    A,
                    b,
                    dummy_p,
                    0.0,
                    enter,
                    row
                )

                row += 1


            else:
                # если получилась строка 0 = 0,
                # она просто лишняя
                if abs(b[row]) < EPS:

                    A.pop(row)
                    b.pop(row)
                    basis.pop(row)

                else:

                    print(
                        "Допустимых решений нет."
                    )
                    return

        else:
            row += 1


    # =========================
    # убираем искусственные столбцы
    # =========================

    keep = []

    for j in range(len(free)):
        if free[j] not in artificial:
            keep.append(j)


    new_A = []

    for i in range(len(A)):

        new_row = []

        for j in keep:
            new_row.append(A[i][j])

        new_A.append(new_row)

    A = new_A


    new_free = []

    for j in keep:
        new_free.append(free[j])

    free = new_free


    # 4. возвращаем исходную Z


    # max переводим в min через умножение на -1
    if task_type == "max":

        min_c = []

        for value in c:
            min_c.append(-value)

    else:

        min_c = c[:]


    # коэффициент каждой переменной в Z
    cost = {}

    # исходные переменные
    for i in range(n):

        cost[
            "x" + str(i + 1)
        ] = min_c[i]


    # дополнительные переменные имеют коэффициент 0
    for name in canonical_names:

        if name not in cost:
            cost[name] = 0.0


    # свободный коэффициент Z
    Q = 0.0

    for i in range(len(basis)):

        Q += (
            cost[basis[i]]
            * b[i]
        )


    # нижняя строка основной таблицы
    p = []

    for j in range(len(free)):

        value = cost[free[j]]

        for i in range(len(basis)):

            value -= (
                cost[basis[i]]
                * A[i][j]
            )

        p.append(value)


    # 5. основная задача


    Q = simplex(
        "Основная задача",
        basis,
        free,
        A,
        b,
        p,
        Q
    )

    if Q is None:
        return


    # 6. формируем ответ

    answer = {}

    # сначала считаем исходные переменные нулевыми
    for i in range(n):

        answer[
            "x" + str(i + 1)
        ] = 0.0


    # базисные берем из столбца b
    for i in range(len(basis)):

        if basis[i] in answer:

            answer[
                basis[i]
            ] = b[i]


    # совсем маленькие числа считаем нулем
    for name in answer:

        if abs(answer[name]) < EPS:
            answer[name] = 0.0


    # если исходно был max,
    # возвращаем нормальный знак
    if task_type == "max":
        Z = -Q

    else:
        Z = Q


    print("\nОТВЕТ")

    for i in range(n):

        name = "x" + str(i + 1)

        print(
            name,
            "=",
            round(answer[name], 6)
        )


    print(
        "Z =",
        round(Z, 6)
    )


# итого!
solve(
    c,
    A,
    signs,
    b,
    task_type
)