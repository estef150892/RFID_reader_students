# RFID_reader_students
Proyecto del lector de RFID para llevar el registro de los alumnos que entran y salen. Proyecto con Pepe (incompleto a falta de fondos)

Materials:
Raspberry pi 3
LCD 16x2 with backlight
Buzzer
2 green LED and 2 red LED

Al leer una tarjeta de identificacion del studiante (RFID card) se busca si esta autorizado o no. Se manda el UID a la pagina del control escolar, la pagina analiza si es un numero valido o no, mandando un True cuando si es valido, en la LCD aaparece un "Autorizado" (Se prenden dos led verdes y suena el buzzer).
El caso contrario es que mande un False aparece en la LCD un "No autorizado" suena el buzzer y se ponen los dos rojos 
Un tercer caso de error de lectura, etc. manda un "Authentication error" a la LCD prenden todos los LEDS y suena el buzzer
