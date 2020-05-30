

def processFile(name: str) -> list:
    f = open(r"data_sample.csv")
    lines = f.read().splitlines()
    f.close()

    ret = []

    for line in lines:
        campos = line.split("|")
        ret.append( {
            "id": campos[0],
            "nombre": campos[1],
            "datos": campos[2]
        })

    return ret

def basic_sort(data): 
    return data['nombre']

def main():
    lines = processFile("data_sample.csv")
    
    for line in lines:
        print(line)

    lines.sort(key = lambda o: o.get('nombre'))

    for line in lines:
        print(line)


if __name__ == '__main__':
    main()