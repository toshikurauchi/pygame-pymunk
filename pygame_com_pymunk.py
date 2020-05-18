# ===== Inicialização =====
# ----- Importa e inicia pacotes
import pygame
import random
import math

# Imports do pymunk
import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

pygame.init()

# ----- Gera tela principal
WIDTH = 480
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Blocos')

# ----- Inicia assets
BLOCK_WIDTH = 100
BLOCK_HEIGHT = 40
block_img = pygame.image.load('block.png').convert_alpha()
block_img = pygame.transform.scale(block_img, (BLOCK_WIDTH, BLOCK_HEIGHT))

# ----- Inicia estruturas de dados
# Definindo os novos tipos
class Block(pygame.sprite.Sprite):
    def __init__(self, img):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.orig_img = img
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.top = 0
        self.speedx = 5
        # Vamos guardar um bloco do pymunk dentro do nosso bloco.
        # Ele será utilizado para saber qual é a posição do nosso bloco.
        self.physical_block = None

    # Criamos esse método ser chamado quando queremos adicionar o bloco na simulação física
    # Inicialmente ele não faz parte da simulação, pois está andando de um lado para o outro
    # no topo da tela. Quando o jogador aperta espaço o bloco passa a fazer parte da
    # simulação física e por isso ele cai.
    def add_physics(self, space):
        # Cria um retângulo com centro na origem (0, 0)
        points = [
            (-BLOCK_WIDTH//2, -BLOCK_HEIGHT//2),
            (-BLOCK_WIDTH//2, BLOCK_HEIGHT//2),
            (BLOCK_WIDTH//2, BLOCK_HEIGHT//2),
            (BLOCK_WIDTH//2, -BLOCK_HEIGHT//2)
        ]
        mass = 1.0  # Define massa do ponto
        moment = pymunk.moment_for_poly(mass, points, (0,0))  # O momento é usado para a simulação física
        body = pymunk.Body(mass, moment)
        body.position = (self.rect.centerx, HEIGHT - self.rect.centery)  # No pymunk a posição é o centro de massa do corpo (body)
        shape = pymunk.Poly(body, points)
        shape.friction = 1  # Define o coeficiente de atrito do corpo
        space.add(body, shape)  # Adiciona o novo corpo no espaço de simulação física
        self.physical_block = body  # Guarda o corpo para usar sua posição na simulação física para atualizar a visualização

    def update(self):
        # Se o corpo já foi adicionado na simulação física
        if self.physical_block:
            # Para de andar na horizontal. Agora todo o movimento será definido pela simulação física
            self.speedx = 0
            # Rotaciona a imagem utilizando o ângulo do corpo na simulação física
            self.image = pygame.transform.rotate(self.orig_img, math.degrees(self.physical_block.angle))
            self.rect = self.image.get_rect()
            # Posiciona a imagem no centro de massa do corpo na simulação física
            center = self.physical_block.position
            self.rect.centerx = center.x
            self.rect.centery = HEIGHT - center.y
        # Se o corpo ainda não foi adicionado na simulação física
        else:
            self.rect.x += self.speedx
            # Rebate se chegar em uma das paredes (inverte o sinal da velocidade)
            if self.rect.left < 0 or self.rect.right > WIDTH:
                self.speedx = -self.speedx

game = True
# Variável para o ajuste de velocidade
clock = pygame.time.Clock()
FPS = 30

# Define espaço físico
space = pymunk.Space()
space.gravity = 0,-1000
space.sleep_time_threshold = 0.5
# Define o chão (sem isso ele cai para sempre)
# As vezes não funciona quando muda muito os parâmetros abaixo
# O chão é um segmento de reta que vai desde -WIDTH até 2*WIDTH
floor = pymunk.Segment(space.static_body, (-WIDTH, 5), (2*WIDTH, 5), 5)
floor.elasticity = 0.5  # Elasticidade do chão
floor.friction = 1  # Coeficiente de atrito do chão
space.add(floor)  # Adiciona o chão na simulação

# Criando um grupo de sprites
all_sprites = pygame.sprite.Group()
last_block = Block(block_img)
all_sprites.add(last_block)

# ===== Loop principal =====
while game:
    clock.tick(FPS)

    # ----- Trata eventos
    for event in pygame.event.get():
        # ----- Verifica consequências
        if event.type == pygame.QUIT:
            game = False
        if event.type == pygame.KEYDOWN:
            # Se o espaço foi apertado, adiciona o bloco na simulação física e
            # cria um novo bloco se movendo no topo da tela
            if event.key == pygame.K_SPACE:
                last_block.add_physics(space)
                last_block = Block(block_img)
                all_sprites.add(last_block)

    # ----- Atualiza estado do jogo
    # Atualizando a posição dos meteoros
    all_sprites.update()
    ### Update physics
    dt = 1./FPS
    space.step(dt)

    # ----- Gera saídas
    window.fill((255, 255, 255))  # Preenche com a cor branca
    # Desenhando meteoros
    all_sprites.draw(window)

    pygame.display.update()  # Mostra o novo frame para o jogador

# ===== Finalização =====
pygame.quit()  # Função do PyGame que finaliza os recursos utilizados

