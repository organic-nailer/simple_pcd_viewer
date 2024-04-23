import sys
import re

class DetectedObject:
    def __init__(
            self,
            filename: str,
            id: int,
            x: float,
            y: float,
            z: float,
            dx: float,
            dy: float,
            dz: float,
            yaw: float,
            label: int,
            score: float,
    ) -> None:
        self.filename = filename
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.yaw = yaw
        self.label = label
        self.score = score
    
    def __str__(self) -> str:
        return f"DetectedObject(filename: {self.filename}, x: {self.x}, y: {self.y}, z: {self.z}, dx: {self.dx}, dy: {self.dy}, dz: {self.dz}, yaw: {self.yaw}, label: {self.label}, score: {self.score})"

def parse_line(line: str) -> DetectedObject:
    match_result = re.fullmatch(r"^/apollo/([^\s]*): object id: (.*), x: (.*), y: (.*), z: (.*), dx: (.*), dy: (.*), dz: (.*), yaw: (.*), label: (.*), score: (.*)\n$", line)
    if match_result is None:
        raise Exception()
    filename = match_result.group(1)
    id = int(match_result.group(2))
    x = float(match_result.group(3))
    y = float(match_result.group(4))
    z = float(match_result.group(5))
    dx = float(match_result.group(6))
    dy = float(match_result.group(7))
    dz = float(match_result.group(8))
    yaw = float(match_result.group(9))
    label = int(match_result.group(10))
    score = float(match_result.group(11))
    return DetectedObject(filename, id, x, y, z, dx, dy, dz, yaw, label, score)

def parse_file(filename: str) -> list[DetectedObject]:
    result = []
    with open(filename, "r") as f:
        while True:
            line = f.readline()
            if line == "":
                break

            if line.startswith("/apollo"):
                obj = parse_line(line)
                result.append(obj)
    return result

def parse_file_to_dict(filename: str) -> dict[str, list[DetectedObject]]:
    result = {}
    with open(filename, "r") as f:
        while True:
            line = f.readline()
            if line == "":
                break

            if line.startswith("/apollo"):
                obj = parse_line(line)
                if obj.filename not in result:
                    result[obj.filename] = []
                result[obj.filename].append(obj)
    return result


def main():
    arg = sys.argv
    if len(arg) < 2:
        return
    
    filename = arg[1]
    obj_list = parse_file(filename)
    for obj in obj_list:
        print(obj)

if __name__ == "__main__":
    main()
