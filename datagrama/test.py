total_bytes = 29423
total_payload = 114

total_pacotes = total_bytes // total_payload

print(total_pacotes)

bytes_restantes = total_bytes - (total_pacotes * total_payload)

print(bytes_restantes)

if bytes_restantes != 0:
    total_pacotes += 1

print(total_pacotes)

handshake = bytearray('oi', 'utf-8')
print(handshake)


n = 100
print(len(n))