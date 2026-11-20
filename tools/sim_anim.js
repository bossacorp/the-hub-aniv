#!/usr/bin/env node
/*
  sim_anim.js — corre show/hub_anim.js fuera de Max (con Node) para probar
  la lógica de escenas y generar vistas previas sin abrir Max.

  Uso:
    node tools/sim_anim.js guion.json > estados.json
    node tools/sim_anim.js --escenas            # {id: nombre} de las escenas definidas

  guion.json: lista de pasos. Cada paso es un mensaje o un avance de tiempo:
    [["scene",1],["snap"],["mix",0.5],["frames",90,30],["scene",2],["frames",120,30]]
  "frames N fps" avanza N cuadros a fps y guarda el estado de las capas en
  cada cuadro. La salida es una lista de cuadros: {capa: {color,scale,position,rotatexyz,enable}}
*/
const fs = require("fs");
const vm = require("vm");
const path = require("path");

const src = fs.readFileSync(path.join(__dirname, "..", "show", "hub_anim.js"), "utf8");
let estado = {};
const sandbox = {
    autowatch: 0, inlets: 1, outlets: 1, messagename: "",
    setinletassist() {}, setoutletassist() {},
    post: (s) => process.stderr.write(String(s)),
    outlet: (n, capa, msg, ...args) => {
        if (n !== 0) return;
        estado[capa] = estado[capa] || {};
        estado[capa][msg] = args;
    },
    Math, Date, module: { exports: {} },
};
vm.createContext(sandbox);
vm.runInContext(src, sandbox, { filename: "hub_anim.js" });
const api = sandbox.module.exports;

if (process.argv[2] === "--escenas") {   // lista {id: nombre} para tools/preview.py
    const out = {};
    for (const k of Object.keys(api.ESCENAS)) out[k] = api.ESCENAS[k].nombre;
    process.stdout.write(JSON.stringify(out));
    process.exit(0);
}
const guion = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const cuadros = [];
for (const paso of guion) {
    const [cmd, ...args] = paso;
    if (cmd === "frames") {
        const [n, fps] = args;
        for (let i = 0; i < n; i++) {
            api.paso(1 / fps);
            cuadros.push(JSON.parse(JSON.stringify(estado)));
        }
    } else if (typeof api[cmd] === "function") {
        api[cmd](...args);
    } else {
        throw new Error("comando desconocido: " + cmd);
    }
}
process.stdout.write(JSON.stringify(cuadros));
