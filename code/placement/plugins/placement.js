var config = {
    type: Phaser.AUTO,
    width: 1024,
    height: 740,
    backgroundColor: '#f1b77c',
    parent: 'tracking-area',
    scene: {
        preload: preload,
        create: create
    },
    physics: {
        default: 'arcade',
        arcade: {
            debug: false
        }
    }
};

var game = new Phaser.Game(config);
var movableObjects = [];
var movableObjectsLabels = [];
var isFirstEpisode = true;
var background;

function preload ()
{
    this.load.setBaseURL('https://raw.githubusercontent.com/coli-saar/placement-game/main');

    this.load.image('pillow', 'images/pillow.png');
    this.load.image('garbage', 'images/garbage.png');
    this.load.image('cap', 'images/caphat.png');
    this.load.image('cowboy', 'images/cowboy-hat.png');
    this.load.image('pants', 'images/pants-trousers.png');

    this.load.image('background1', 'images/background1.png');
    this.load.image('background2', 'images/background2.jpg');
}

function makeObject(self, width, height, id, scale) {
    var x = rand(width);
    var y = rand(height);
    var ret = self.add.image(x, y, id).setScale(scale);

    ret.on('pointerover', function () {
        ret.setTint(0xdddddd);
    });

    ret.on('pointerout', function () {
        ret.clearTint();
    });

    ret.setInteractive();
    self.input.setDraggable(ret);
    movableObjects.push(ret);

    movableObjectsLabels.push(id);

    return ret;
}

function rand(maxValue) {
    return Math.floor(maxValue * (Math.random() * 0.8 + 0.1));
}

function create (){

    var movableObjectsGroup = this.physics.add.group();

    console.log(isFirstEpisode);

    if (isFirstEpisode == true) {
        background = this.add.image(507, 373, 'background1').setScale(0.9);
    } else {
        background = this.add.image(512, 384, 'background2').setScale(1.2);
    };

    // movable objects
    let { width, height } = this.sys.game.canvas;

    // var knife = makeObject(this, width, height, 'knife', 0.20);
    // var pan = makeObject(this, width, height, 'pan', 0.3);
    // var tp = makeObject(this, width, height, 'tp', 0.3);

    var pillow = makeObject(this, width, height, 'pillow', 0.32);
    var garbage = makeObject(this, width, height, 'garbage', 0.55);
    var cap = makeObject(this, width, height, 'cap', 0.3);
    // var vacuum = makeObject(this, width, height, 'vacuum', 0.47);
    var cowboy = makeObject(this, width, height, 'cowboy', 0.3);
    var pants = makeObject(this, width, height, 'pants', 0.4);

    var objects_board = get_object_position();
    socket.emit("message_command",
        {
            "command": {
                "event": "board_logging",
                "board": objects_board
                // [{"name": "knife", "x": 2, "y":6}, {"name": "tp", "x": 6, "y": 4}]
            },
            "room": self_room
        }
    );

    movableObjectsGroup.add(pillow);
    movableObjectsGroup.add(garbage);
    movableObjectsGroup.add(cap);
    // movableObjectsGroup.add(vacuum);
    movableObjectsGroup.add(cowboy);
    movableObjectsGroup.add(pants);

    // Enable physics and set collisions
    this.physics.world.enable(movableObjectsGroup);
    this.physics.add.collider(movableObjectsGroup);

    this.input.on('drag', function (pointer, gameObject, dragX, dragY) {
        gameObject.x = dragX;
        gameObject.y = dragY;
    });

    this.input.on('dragstart', function (pointer, gameObject) {
        // the gripped object is brought to the front
        bringToFront(gameObject);

        // saving the starting position in case the object gets placed on top of another and needs to snap back
        gameObject.setData('previousX', gameObject.x); 
        gameObject.setData('previousY', gameObject.y);
    });

    this.input.on('dragend', function (pointer, gameObject) {
        var overlappingObject = movableObjects.find((object) => {
        return object !== gameObject && isOverlapExceedingThreshold(gameObject, object, 0.1);
        });

        // if the object is exceeding the overlapping threshold, return it to the previous position
        if (overlappingObject) {
            gameObject.x = gameObject.getData('previousX');
            gameObject.y = gameObject.getData('previousY');
        };

        var objects_board = get_object_position();
        socket.emit("message_command",
            {
                "command": {
                    "event": "board_logging",
                    "board": objects_board
                },
                "room": self_room
            }
        )
    });
}

function get_object_position(){
    var positionedObjects = [];

    for (let i = 0; i < movableObjects.length; i++){
        var tempPositions = {};
        tempPositions['name'] = movableObjectsLabels[i];
        tempPositions['x'] = movableObjects[i].x;
        tempPositions['y'] = movableObjects[i].y;

        positionedObjects.push(tempPositions);
    }
    return positionedObjects;
}

function bringToFront(gameObject) {
    gameObject.depth = 1;

    movableObjects.forEach((object) => {
        if (object !== gameObject) {
            object.depth = 0;
        }
    });
}
// a function that determines whether the most recently moved object (A) is placed on top of another object (B) by checking if the area of A covering B exceeds a threshold
// returns: bool 
function isOverlapExceedingThreshold(object1, object2, threshold) {
    var bounds1 = object1.getBounds();
    var bounds2 = object2.getBounds();

    var intersectionWidth = Math.min(bounds1.right, bounds2.right) - Math.max(bounds1.x, bounds2.x);
    var intersectionHeight = Math.min(bounds1.bottom, bounds2.bottom) - Math.max(bounds1.y, bounds2.y);

    var overlapArea = Math.max(0, intersectionWidth) * Math.max(0, intersectionHeight);
    var object1Area = bounds1.width * bounds1.height;

    return overlapArea / object1Area >= threshold;
}

function resetGameState() {
    // Reset movable objects to their initial positions
    movableObjects.forEach((object, index) => {
        object.x = rand(width);
        object.y = rand(height);
    });

    // Change the background image based on the game state

    background.destroy(); // Destroy the current background

    background = this.add.image(620, 408, 'background2').setScale(1);

    isFirstEpisode = false;
    create();

}


$(`#submit_button`).click(() => {
    console.log("SUBMITTING")
    socket.emit("message_command",
        {
            "command": "stop",
            "room": self_room,
            "user_id": self_user
        }
    )
})

$(document).ready(function () {
    socket.on("command", (data) => {
        if (typeof (data.command) === "object") {
            switch(data.command.event){
                // // define if needed
                case "new_episode": // defined in the bot
                    game.destroy(true, false)
                    game = null;
                    movableObjects = null;
                    movableObjectsLabels = null;
                    objects_board = null;


                    var config = {
                        type: Phaser.AUTO,
                        width: 1024,
                        height: 740,
                        backgroundColor: '#f1b77c',
                        parent: 'tracking-area',
                        scene: {
                            preload: preload,
                            create: create
                        },
                        physics: {
                            default: 'arcade',
                            arcade: {
                                debug: false
                            }
                        }
                    };
                    
                    game = new Phaser.Game(config);
                    movableObjects = [];
                    movableObjectsLabels = [];
                    isFirstEpisode = false;
                    preload();
                    create();
                    break;

            }
        }
    });
})