import random, pygame, sys
class CHIP8:
    def __init__(self):
        pygame.init()
        self.keypad = [pygame.K_x, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_z, pygame.K_c, pygame.K_4, pygame.K_r, pygame.K_f, pygame.K_v]
        self.clock = pygame.time.Clock()
        self.offColour = (0, 0, 0)
        self.onColour = (255, 255, 255)
        self.DISPLAYSURF = pygame.display.set_mode((640, 320))
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.opcode = 0x0000
        self.IR = 0x000
        self.PC = 0x200
        self.graphics = [0] * 2048
        self.dTimer = 0
        self.sTimer = 0
        self.stack = [0] * 16
        self.SP = 0x0
        self.key = [0] * 16
        chip8fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
            ]
        for i in range(len(chip8fontset)):
            self.memory[i + 0x0] = chip8fontset[i]
    def loadProgram(self, program):
        for i in range(len(program)):
            self.memory[i + 0x200] = program[i]
    def updateDisplay(self):
        self.DISPLAYSURF.fill(self.offColour)
        for i in range(2048):
            if self.graphics[i]:
                pygame.draw.rect(self.DISPLAYSURF, self.onColour, ((i % 64) * 10, ((i - (i % 64)) // 64) * 10, 10, 10))
        pygame.display.update()
    def cycle(self):
        op1 = self.memory[self.PC]
        op2 = self.memory[self.PC + 1]
        op1 = op1 << 8
        self.opcode = op1 | op2
        firstDigit = self.opcode & 0xF000
        otherDigits = self.opcode & 0x0FFF
        if firstDigit == 0x0000:
            if self.opcode == 0x00E0:
                self.graphics = [0] * 2048
                self.PC += 2
            elif self.opcode == 0x00EE:
                self.PC = self.stack[self.SP - 1] + 2
                self.stack[self.SP] = 0x000
                self.SP -= 1
            else:
                self.PC += 2
                
        elif firstDigit == 0x1000:
            self.PC = otherDigits
            
        elif firstDigit == 0x2000:
            self.stack[self.SP] = self.PC
            self.SP += 1
            self.PC = otherDigits
            
        elif firstDigit == 0x3000:
            if self.V[(otherDigits & 0x0F00) >> 8] == otherDigits & 0x00FF:
                self.PC += 4
            else:
                self.PC += 2
        
        elif firstDigit == 0x4000:
            if self.V[(otherDigits & 0x0F00) >> 8] != otherDigits & 0x00FF:
                self.PC += 4
            else:
                self.PC += 2
        elif firstDigit == 0x5000:
            if self.V[(otherDigits & 0x0F00) >> 8] == self.V[(otherDigits & 0x00F0) >> 4]:
                self.PC += 4
            else:
                self.PC += 2
        
        elif firstDigit == 0x6000:
            self.V[(otherDigits & 0x0F00) >> 8] = otherDigits & 0x00FF
            self.PC += 2
        
        elif firstDigit == 0x7000:
            self.V[(otherDigits & 0x0F00) >> 8] += otherDigits & 0x00FF
            self.PC += 2
        
        elif firstDigit == 0x8000:
            lastDigit = self.opcode & 0x000F
            if lastDigit == 0x0000:
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x00F0) >> 4]
            elif lastDigit == 0x0001:
                self.V[(self.opcode & 0x0F00) >> 8] |= self.V[(self.opcode & 0x00F0) >> 4]
            elif lastDigit == 0x0002:
                self.V[(self.opcode & 0x0F00) >> 8] &= self.V[(self.opcode & 0x00F0) >> 4]
            elif lastDigit == 0x0003:
                self.V[(self.opcode & 0x0F00) >> 8] ^= self.V[(self.opcode & 0x00F0) >> 4]
            elif lastDigit == 0x0004:
                XYsum = self.V[(self.opcode & 0x0F00) >> 8] + self.V[(self.opcode & 0x00F0) >> 4]
                if XYsum > 0xFF:
                    self.V[0xF] = 0x01
                else:
                    self.V[0xF] = 0x00
                self.V[(self.opcode & 0x0F00) >> 8] = (XYsum & 0xFF)
            elif lastDigit == 0x0005:
                XYdif = self.V[(self.opcode & 0x0F00) >> 8] - self.V[(self.opcode & 0x00F0) >> 4]
                if XYdif >= 0:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[(self.opcode & 0x0F00) >> 8] = XYdif & 0xFF
            elif lastDigit == 0x0006:
                self.V[0xF] = (self.V[(otherDigits & 0x0F00) >> 8]) & 0x1
                self.V[(otherDigits & 0x0F00) >> 8] = (self.V[(otherDigits & 0x0F00) >> 8] >> 1)
            elif lastDigit == 0x0007:
                YXdif = self.V[(self.opcode & 0x00F0) >> 4] - self.V[(self.opcode & 0x0F00) >> 8]
                self.V[(otherDigits & 0x0F00) >> 8] = YXdif & 0xFF
                if YXdif >= 0:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
            elif lastDigit == 0x000E:
                self.V[0xF] = (self.V[(otherDigits & 0x0F00) >> 8]) & 0b10000000
                self.V[(otherDigits & 0x0F00) >> 8] = (self.V[(otherDigits & 0x0F00) >> 8]) << 1
            self.PC += 2
        
        elif firstDigit == 0x9000:
            if self.V[(otherDigits & 0x0F00) >> 8] != self.V[(otherDigits & 0x00F0) >> 4]:
                self.PC += 4
            else:
                self.PC += 2
        
        elif firstDigit == 0xA000:
            self.IR = otherDigits
            self.PC += 2
        
        elif firstDigit == 0xB000:
            self.PC = self.V[0] + otherDigits
        
        elif firstDigit == 0xC000:
            self.V[(otherDigits & 0x0F00) >> 8] =  random.randint(-1, 0xFF) & (otherDigits & 0xFF)
            self.PC += 2
        
        elif firstDigit == 0xD000:
            posX = self.V[(otherDigits & 0x0F00) >> 8]
            posY = self.V[(otherDigits & 0x00F0) >> 4]
            spriteHeight = otherDigits & 0xF
            flipped = False
            for yOff in range(spriteHeight):
                row = self.memory[self.IR + yOff]
                for xOff in range(8):
                    #print(posX, posY, xOff, yOff)
                    #print(posX + xOff + (64 * posY + yOff))
                    self.graphics[(posX + xOff + (64 * (posY + yOff))) % 2048] ^= (((row & (1 << (7 - xOff))) >> (7 - xOff)))
                    #print((row & (1 << (7 - xOff))))
                    #print(1 << 7, 7 - xOff)
                    if (row & (1 << (7 - xOff))) and not self.graphics[(posX + xOff + (64 * (posY + yOff))) % 2048]:
                        flipped = True
                    
            if flipped:
                self.V[0xF] = 1
            else:
                self.V[0xF] = 0
            self.PC += 2
            self.updateDisplay()
        
        elif firstDigit == 0xE000:
            lastDigits = self.opcode & 0xFF
            X = self.opcode & 0xF00
            X >>= 8
            if lastDigits == 0x9E:
                if self.key[self.V[X]]:
                    self.PC += 4
                else:
                    self.PC += 2
            if lastDigits == 0xA1:
                if not self.key[self.V[X]]:
                    self.PC += 4
                else:
                    self.PC += 2
        
        elif firstDigit == 0xF000:
            lastDigits = self.opcode & 0xFF
            X = self.opcode & 0xF00
            X >>= 8
            if lastDigits == 0x07:
                self.V[X] = self.dTimer
            elif lastDigits == 0x0A:
                done = False
                while not done:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYUP:
                            if event.key in self.keypad:
                                done = True
                                self.V[X] = self.keypad.index(event.key)
            elif lastDigits == 0x15:
                self.dTimer = self.V[X]
            elif lastDigits == 0x18:
                pass
            elif lastDigits == 0x1E:
                newI = self.IR + X
                if newI > 0xFFF:
                    newI &= 0xFFF
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.IR = newI
            elif lastDigits == 0x29:
                self.IR = self.V[X] * 5
            elif lastDigits == 0x33:
                num = self.V[X]
                num100 = num - num % 100
                num10 = num - num % 10
                num10 -= num100
                num1 = num % 10
                num100 //= 100
                num10 //= 10
                self.memory[self.IR] = num100
                self.memory[self.IR + 1] = num10
                self.memory[self.IR + 2] = num1
            elif lastDigits == 0x55:
                for i in range(X + 1):
                     self.memory[self.IR + i] = self.V[i]
            elif lastDigits == 0x65:
                for i in range(X + 1):
                    self.V[i] = self.memory[self.IR + i]
                
            self.PC += 2
        #print(self.PC, self.V, hex(self.opcode))

x = CHIP8()
byteCode = []
with open(input("Choose a .ch8 file to open\n>>> "), mode = "rb") as file:
    for each in file.readlines():
        for byte in each:
            byteCode.append(byte)

#byteCode = [0xF0, 0x29, 0xD0, 0x05]

#print(len(byteCode))
for i in range(len(byteCode) // 2):
    p1 = byteCode[2 * i]
    p1 <<= 8
    p2 = byteCode[2 * i + 1]
    print(hex(p1 | p2))
x.loadProgram(byteCode)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    currKeys = pygame.key.get_pressed()
    for each in range(len(x.keypad)):
        if currKeys[x.keypad[each]]:
            x.key[each] = 1
        else:
            x.key[each] = 0
    x.cycle()
    if x.dTimer > 0:
        x.dTimer -= 1
    if x.sTimer > 0:
        x.sTimer -= 1
    x.clock.tick(60)
