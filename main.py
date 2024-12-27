from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionNode, CollisionRay
from panda3d.core import CollisionBox, CollisionSphere, Vec3, BitMask32
from panda3d.core import WindowProperties
from panda3d.core import Point3
import math


class FPSGame(ShowBase):
    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)  # Cache le curseur
        self.win.requestProperties(props)

        # Charger un modèle de terrain
        self.environment = self.loader.loadModel("models/environment")
        self.environment.reparentTo(self.render)
        self.environment.setScale(10, 10, 10)
        self.environment.setPos(-8, 42, 0)

        # Position initiale du joueur
        self.camera.setPos(0, 0, 2)

        # Variables de mouvement
        self.speed = 5
        self.mouse_sensitivity = 0.2
        self.key_map = {"forward": False, "backward": False, "left": False, "right": False}

        # Détecteur de collisions
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        # Ajouter une boîte de collision au joueur
        player_collider = self.camera.attachNewNode(CollisionNode("player"))
        player_collider.node().addSolid(CollisionBox(Point3(0, 0, 1), 0.5, 0.5, 1))
        player_collider.node().setFromCollideMask(BitMask32.bit(0))
        player_collider.node().setIntoCollideMask(BitMask32.allOff())
        self.pusher.addCollider(player_collider, self.camera)
        self.cTrav.addCollider(player_collider, self.pusher)

        # Ajout d'un mur avec collision
        self.wall = self.loader.loadModel("models/box")
        self.wall.setScale(2, 2, 2)
        self.wall.setPos(5, 5, 1)
        self.wall.reparentTo(self.render)

        wall_collider = self.wall.attachNewNode(CollisionNode("wall"))
        wall_collider.node().addSolid(CollisionBox(Point3(0, 0, 0), 2, 2, 2))
        wall_collider.node().setFromCollideMask(BitMask32.allOff())
        wall_collider.node().setIntoCollideMask(BitMask32.bit(0))

        # Gestion des entrées utilisateur
        self.accept("w", self.update_key_map, ["forward", True])
        self.accept("s", self.update_key_map, ["backward", True])
        self.accept("a", self.update_key_map, ["left", True])
        self.accept("d", self.update_key_map, ["right", True])
        self.accept("w-up", self.update_key_map, ["forward", False])
        self.accept("s-up", self.update_key_map, ["backward", False])
        self.accept("a-up", self.update_key_map, ["left", False])
        self.accept("d-up", self.update_key_map, ["right", False])

        # Gestion des tirs
        self.accept("mouse1", self.shoot)

        # Tâches régulières
        self.taskMgr.add(self.update_camera, "update_camera")
        self.taskMgr.add(self.move_player, "move_player")

    def update_key_map(self, key, value):
        self.key_map[key] = value

    def move_player(self, task):
        dt = globalClock.getDt()
        move = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move.y += self.speed * dt
        if self.key_map["backward"]:
            move.y -= self.speed * dt
        if self.key_map["left"]:
            move.x -= self.speed * dt
        if self.key_map["right"]:
            move.x += self.speed * dt
        self.camera.setPos(self.camera, move)
        return task.cont

    def update_camera(self, task):
        # Capture les mouvements de la souris pour la rotation
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        self.win.movePointer(0, int(self.win.getXSize() / 2), int(self.win.getYSize() / 2))

        delta_x = (x - self.win.getXSize() / 2) * self.mouse_sensitivity
        delta_y = (y - self.win.getYSize() / 2) * self.mouse_sensitivity

        # Mise à jour des angles de rotation
        self.camera.setH(self.camera.getH() + delta_x)
        self.camera.setP(self.camera.getP() + delta_y)
        return task.cont

    def shoot(self):
        # Raycasting pour détecter un tir
        ray = CollisionRay()
        ray.setOrigin(self.camera.getPos())
        ray.setDirection(self.camera.getQuat().getForward())

        ray_node = CollisionNode("ray")
        ray_node.addSolid(ray)
        ray_node.setFromCollideMask(BitMask32.bit(0))
        ray_node.setIntoCollideMask(BitMask32.allOff())

        ray_np = self.camera.attachNewNode(ray_node)
        self.cTrav.addCollider(ray_np, self.pusher)

        print("Tir !")


# Lancer le jeu
game = FPSGame()
game.run()
