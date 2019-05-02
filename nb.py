
x = {"x":"123", "y":"***Replied sticker/image***"}
y = {"x":"13", "y":"asddddd"}
z = [x,y]

for i  in z:
    if "Replied sticker" in i["y"]:
        z.remove(i)

print(z)