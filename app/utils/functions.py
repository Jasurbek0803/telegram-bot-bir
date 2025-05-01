import os

TESTS_FILE = "tests.txt"


def find_test_by_code(code: str):
    with open(TESTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" not in line or "*" not in line:
                continue

            try:
                user_id_part, rest = line.split(":", 1)
                parts = rest.split("*")
                if len(parts) != 4:
                    continue
                maxsus_kod, javoblar, oquv_markaz, test_egasi = parts
                if maxsus_kod == code:
                    return {
                        "code": maxsus_kod,
                        "answers": javoblar.upper(),
                        "center": oquv_markaz,
                        "owner": test_egasi
                    }
            except ValueError:
                continue
    return None
