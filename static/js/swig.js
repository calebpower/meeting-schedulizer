function SketchArt() {

    let canvas;
    let context;
    let width;
    let height;
    let mouse = {x: window.innerWidth / 2, y: window.innerHeight};
    this.mouse = mouse;

    let interval;
    let vms = [];
    let MAX_NUM = 100;
    let N = 80;
    let px = window.innerWidth / 2;
    let py = window.innerHeight;

    this.initialize = function () {
        canvas = document.getElementById("canvas");
        context = canvas.getContext('2d');

        width = window.innerWidth;
        height = window.innerHeight;

        canvas.width = width;
        canvas.height = height;

        canvas.addEventListener('touchmove', TouchMove, false);
        canvas.addEventListener('mousemove', MouseMove, false);
        canvas.addEventListener('click', MouseDown, false);
        let interval = setInterval(Sketch, 20);

    };

    let Sketch = function () {
    	let len = vms.length;
        let i;
        for (i = 0; i < len; i++) {
            let o = vms[i];
            if (o.count < N) {
                SketchArt(o);
                o.count++;
                //This looks a tad hacky........................xD
            } else {
                len--;
                vms.splice(i, 1);
                i--;
            }
        }
        Check();
    };

    let SketchArt = function (obj) {
        if (Math.random() > 0.9) {
            obj.tmt.rotate(-obj.r * 2);
            obj.r *= -1;
        }
        obj.vmt.prependMatrix(obj.tmt);
        let cc1x = -obj.w * obj.vmt.c + obj.vmt.tx;
        let cc1y = -obj.w * obj.vmt.d + obj.vmt.ty;
        let pp1x = (obj.c1x + cc1x) / 2;
        let pp1y = (obj.c1y + cc1y) / 2;

        let cc2x = obj.w * obj.vmt.c + obj.vmt.tx;
        let cc2y = obj.w * obj.vmt.d + obj.vmt.ty;
        let pp2x = (obj.c2x + cc2x) / 2;
        let pp2y = (obj.c2y + cc2y) / 2;

        context.fillStyle = '#000000';
        context.strokeStyle = '#000000';
        context.beginPath();
        context.moveTo(obj.p1x, obj.p1y);
        context.quadraticCurveTo(obj.c1x, obj.c1y, pp1x, pp1y);
        context.lineTo(pp2x, pp2y);
        context.quadraticCurveTo(obj.c2x, obj.c2y, obj.p2x, obj.p2y);

        //context.stroke();
        context.closePath();
        context.fill();
        obj.c1x = cc1x;
        obj.c1y = cc1y;
        obj.p1x = pp1x;
        obj.p1y = pp1y;
        obj.c2x = cc2x;
        obj.c2y = cc2y;
        obj.p2x = pp2x;
        obj.p2y = pp2y;
    };

    let Check = function () {
        let x0 = mouse.x;
        let y0 = mouse.y;
        let vx = x0 - px;
        let vy = y0 - py;

        let len = Math.min(Magnitude(vx, vy), 50);
        if (len < 10) {
            return;
        }
        let matrix = new Matrix2D();
        matrix.rotate((Math.atan2(vy, vx)));
        matrix.translate(x0, y0);

        createArt(matrix, len);
        context.beginPath();
        context.strokeStyle = '#000000';
        context.moveTo(px, py);
        context.lineTo(x0, y0);
        context.stroke();
        context.closePath();

        px = x0;
        py = y0;
    };

    let createArt = function (mtx, len) {
        let angle = Math.random() * (Math.PI / 6 - Math.PI / 64) + Math.PI / 64;
        if (Math.random() > 0.5) {
            angle *= -1;
        }
        let tmt = new Matrix2D();
        tmt.scale(0.95, 0.95);
        tmt.rotate(angle);
        tmt.translate(len, 0);

        let w = 0.5;
        let obj = new Art();

        obj.c1x = (-w * mtx.c + mtx.tx);
        obj.p1x = (-w * mtx.c + mtx.tx);
        obj.c1y = (-w * mtx.d + mtx.ty);
        obj.p1y = (-w * mtx.d + mtx.ty);

        obj.c2x = (w * mtx.c + mtx.tx);
        obj.p2x = (w * mtx.c + mtx.tx);
        obj.c2y = (w * mtx.d + mtx.ty);
        obj.p2y = (w * mtx.d + mtx.ty);

        obj.vmt = mtx;
        obj.tmt = tmt;
        obj.r = angle;
        obj.w = len / 20;
        obj.count = 0;

        vms.push(obj);

        if (vms.length > MAX_NUM) {
            vms.shift();
        }
    };
    let Art = function () {
        this.c1x = null;
        this.c1y = null;
        this.c2x = null;
        this.c2y = null;
        this.p1x = null;
        this.p1y = null;
        this.p2x = null;
        this.p2y = null;
        this.w = null;
        this.r = null;
        this.count = null;
        this.vmt = null;
        this.tmt = null;

    };
    let fadeScreen = function () {
        context.fillStyle = 'rgba(255, 255, 255, 0.02)';
        context.beginPath();
        context.rect(0, 0, width, height);
        context.closePath();
        context.fill();
    };
    //i think this works........
    let MouseDown = function (e) {
        e.preventDefault();
        canvas.width = canvas.width;
        vms = [];
    };

    let MouseMove = function (e) {
        mouse.x = e.layerX - canvas.offsetLeft;
        mouse.y = e.layerY - canvas.offsetTop;
    };

    let TouchMove = function (e) {
        e.preventDefault();
        mouse.x = e.targetTouches[0].pageX - canvas.offsetLeft;
        mouse.y = e.targetTouches[0].pageY - canvas.offsetTop;
    };

    //Returns Magnitude
    let Magnitude = function (x, y) {
        return Math.sqrt((x * x) + (y * y));
    }

}
(function (window) {
    let Matrix2D = function (a, b, c, d, tx, ty) {
        this.initialize(a, b, c, d, tx, ty);
    };
    let p = Matrix2D.prototype;
    Matrix2D.identity = null;
    Matrix2D.DEG_TO_RAD = Math.PI / 180;

    p.a = 1;
    p.b = 0;
    p.c = 0;
    p.d = 1;
    p.tx = 0;
    p.ty = 0;
    p.alpha = 1;
    p.shadow = null;
    p.compositeOperation = null;
    p.initialize = function (a, b, c, d, tx, ty) {
        if (a != null) {
            this.a = a;
        }
        this.b = b || 0;
        this.c = c || 0;
        if (d != null) {
            this.d = d;
        }
        this.tx = tx || 0;
        this.ty = ty || 0;
    };

    p.prepend = function (a, b, c, d, tx, ty) {
        let n11 = a * this.a + b * this.c;
        let n12 = a * this.b + b * this.d;
        let n21 = c * this.a + d * this.c;
        let n22 = c * this.b + d * this.d;
        let n31 = tx * this.a + ty * this.c + this.tx;
        let n32 = tx * this.b + ty * this.d + this.ty;

        this.a = n11;
        this.b = n12;
        this.c = n21;
        this.d = n22;
        this.tx = n31;
        this.ty = n32;
    };

    p.append = function (a, b, c, d, tx, ty) {
        let a1 = this.a;
        let b1 = this.b;
        let c1 = this.c;
        let d1 = this.d;

        this.a = a * a1 + b * c1;
        this.b = a * b1 + b * d1;
        this.c = c * a1 + d * c1;
        this.d = c * b1 + d * d1;
        this.tx = tx * a1 + ty * c1 + this.tx;
        this.ty = tx * b1 + ty * d1 + this.ty;

    };

    p.prependMatrix = function (matrix) {
        this.prepend(matrix.a, matrix.b, matrix.c, matrix.d, matrix.tx, matrix.ty);
        this.prependProperties(matrix.alpha, matrix.shadow, matrix.compositeOperation);
    };

    p.appendMatrix = function (matrix) {
        this.append(matrix.a, matrix.b, matrix.c, matrix.d, matrix.tx, matrix.ty);
        this.appendProperties(matrix.alpha, matrix.shadow, matrix.compositeOperation);
    };

    p.prependTransform = function (x, y, scaleX, scaleY, rotation, skewX, skewY, regX, regY) {
        if (rotation % 360) {
            let r = rotation * Matrix2D.DEG_TO_RAD;
            let cos = Math.cos(r);
            let sin = Math.sin(r);
        } else {
            cos = 1;
            sin = 0;
        }

        if (regX || regY) {
            this.tx -= regX;
            this.ty -= regY;
        }
        if (skewX || skewY) {
            skewX *= Matrix2D.DEG_TO_RAD;
            skewY *= Matrix2D.DEG_TO_RAD;
            this.prepend(cos * scaleX, sin * scaleX, -sin * scaleY, cos * scaleY, 0, 0);
            this.prepend(Math.cos(skewY), Math.sin(skewY), -Math.sin(skewX), Math.cos(skewX), x, y);
        } else {
            this.prepend(cos * scaleX, sin * scaleX, -sin * scaleY, cos * scaleY, x, y);
        }

    };

    p.appendTransform = function (x, y, scaleX, scaleY, rotation, skewX, skewY, regX, regY) {
        if (rotation % 360 == 0 && scaleX == 1 && scaleY == 1 && skewX == 0 && skewY == 0) {
            this.tx += x - regX;
            this.ty += y - regY;
            return;
        }

        if (rotation % 360) {
            let r = rotation * Matrix2D.DEG_TO_RAD;
            let cos = Math.cos(r);
            let sin = Math.sin(r);
        } else {
            cos = 1;
            sin = 0;
        }

        if (skewX || skewY) {
            // TODO: can this be combined into a single append?
            skewX *= Matrix2D.DEG_TO_RAD;
            skewY *= Matrix2D.DEG_TO_RAD;
            this.append(Math.cos(skewY), Math.sin(skewY), -Math.sin(skewX), Math.cos(skewX), x, y);
            this.append(cos * scaleX, sin * scaleX, -sin * scaleY, cos * scaleY, 0, 0);
        } else {
            this.append(cos * scaleX, sin * scaleX, -sin * scaleY, cos * scaleY, x, y);
        }

        if (regX || regY) {
            // prepend the registration offset:
            this.tx -= regX * this.a + regY * this.c;
            this.ty -= regX * this.b + regY * this.d;
        }
    };

    p.rotate = function (angle) {
        let sin = Math.sin(angle);
        let cos = Math.cos(angle);
        let n11 = cos * this.a + sin * this.c;
        let n12 = cos * this.b + sin * this.d;
        let n21 = -sin * this.a + cos * this.c;
        let n22 = -sin * this.b + cos * this.d;
        this.a = n11;
        this.b = n12;
        this.c = n21;
        this.d = n22;
    };

    p.skew = function (skewX, skewY) {
        skewX = skewX * Matrix2D.DEG_TO_RAD;
        skewY = skewY * Matrix2D.DEG_TO_RAD;
        this.append(Math.cos(skewY), Math.sin(skewY), -Math.sin(skewX), Math.cos(skewX), 0, 0);
    };

    p.scale = function (x, y) {
        this.a *= x;
        this.d *= y;
        this.tx *= x;
        this.ty *= y;
    };

    p.translate = function (x, y) {
        this.tx += x;
        this.ty += y;
    };

    p.identity = function () {
        this.alpha = this.a = this.d = 1;
        this.b = this.c = this.tx = this.ty = 0;
        this.shadow = this.compositeOperation = null;
    };

    p.invert = function () {
        let a1 = this.a;
        let b1 = this.b;
        let c1 = this.c;
        let d1 = this.d;
        let tx1 = this.tx;
        let n = a1 * d1 - b1 * c1;

        this.a = d1 / n;
        this.b = -b1 / n;
        this.c = -c1 / n;
        this.d = a1 / n;
        this.tx = (c1 * this.ty - d1 * tx1) / n;
        this.ty = -(a1 * this.ty - b1 * tx1) / n;
    };

    p.isIdentity = function () {
        return this.tx == 0 && this.ty == 0 && this.a == 1 && this.b == 0 && this.c == 0 && this.d == 1;
    };

    p.decompose = function (target) {
        // even when scale is negative
        if (target == null) {
            target = {};
        }
        target.x = this.tx;
        target.y = this.ty;
        target.scaleX = Math.sqrt(this.a * this.a + this.b * this.b);
        target.scaleY = Math.sqrt(this.c * this.c + this.d * this.d);

        let skewX = Math.atan2(-this.c, this.d);
        let skewY = Math.atan2(this.b, this.a);

        if (skewX == skewY) {
            target.rotation = skewY / Matrix2D.DEG_TO_RAD;
            if (this.a < 0 && this.d >= 0) {
                target.rotation += (target.rotation <= 0) ? 180 : -180;
            }
            target.skewX = target.skewY = 0;
        } else {
            target.skewX = skewX / Matrix2D.DEG_TO_RAD;
            target.skewY = skewY / Matrix2D.DEG_TO_RAD;
        }
        return target;
    };

    p.reinitialize = function (a, b, c, d, tx, ty, alpha, shadow, compositeOperation) {
        this.initialize(a, b, c, d, tx, ty);
        this.alpha = alpha || 1;
        this.shadow = shadow;
        this.compositeOperation = compositeOperation;
        return this;
    };

    p.appendProperties = function (alpha, shadow, compositeOperation) {
        this.alpha *= alpha;
        this.shadow = shadow || this.shadow;
        this.compositeOperation = compositeOperation || this.compositeOperation;
    };

    p.prependProperties = function (alpha, shadow, compositeOperation) {
        this.alpha *= alpha;
        this.shadow = this.shadow || shadow;
        this.compositeOperation = this.compositeOperation || compositeOperation;
    };

    p.clone = function () {
        let mtx = new Matrix2D(this.a, this.b, this.c, this.d, this.tx, this.ty);
        mtx.shadow = this.shadow;
        mtx.alpha = this.alpha;
        mtx.compositeOperation = this.compositeOperation;
        return mtx;
    };


    p.toString = function () {
        return "[Matrix2D (a=" + this.a + " b=" + this.b + " c=" + this.c + " d=" + this.d + " tx=" + this.tx + " ty=" + this.ty + ")]";
    };

    // this has to be populated after the class is defined:
    Matrix2D.identity = new Matrix2D(1, 0, 0, 1, 0, 0);

    window.Matrix2D = Matrix2D;
    }(window));

    let app, interval, count;

    function App() {
    count++;
    if (count % 2 == 0) {
        app.mouse.y -= 40
    } else {
        app.mouse.y += 40;
     }

    if (count > 30) {
        window.clearInterval(interval);
        }
    }

    setTimeout(function () {
        app = new SketchArt();
        app.initialize();
        count = 0;
        interval = setInterval(App, 60);
    }, 10);