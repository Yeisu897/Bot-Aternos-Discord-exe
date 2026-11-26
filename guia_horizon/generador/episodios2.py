# Guion v2 (actualizado al código de Horizonbeta 1.69): más corto, más visual.
# L(dice, viñeta, iconos, vis, fx)
#   vis: ("hud", foco) · ("cuadro", n) · ("items", [iconos]) · ("receta", [9 casillas], resultado)
#        ("big", "TEXTO", "subtexto") · ("cmd", "/comando")
#   fx:  nieve · brasas · corazones · sangre · confeti · burbujas · estrellas · temblor · rayos
#   En recetas: nombre de ítem del addon = su ícono; cualquier otro texto = casilla con texto; "" = vacía.
def L(say, bul=None, ics=(), v=None, fx=None):
    return (say, bul, list(ics), v, fx)

EPISODIOS = [
# ════════════════════════════════════════════ 1
dict(n=1, titulo="Primeros pasos", sub="Tu HUD, el calor, la sed y la infección", escenas=[
 dict(t="¡Bienvenida a Horizon!", icon="libro", lineas=[
  L("¡Hola, hola! Soy Yei, tu guía de Horizon. ¡Y en esta serie te enseño todo para sobrevivir en este addon!", None, [], ("cuadro", 21), "estrellas"),
  L("Horizon cambia todo: calor, sed, zombis que infectan, mobs rarísimos, dinero, clanes, bodas, catástrofes... ¡y hasta un viaje al espacio!", "Supervivencia mucho más difícil", [], ("items", ["bloqueador", "pastilla", "ficha_arcoiris", "anillo_boda", "endersita_casco", "hm_pez_leyenda"])),
  L("Al entrar por primera vez te dan un kit de inicio: un bloqueador solar y una botella de agua. ¡Úsalos bien!", "Kit de inicio: bloqueador + agua", ["bloqueador", "hm_agua_hervida"], ("items", ["bloqueador", "hm_agua_hervida"])),
  L("Y tienes el Libro, con toda la guía. Ábrelo con /guia, y si lo pierdes, /hm libro te da otro.", "El Libro: /guia · /hm libro", ["libro"], ("cmd", "/guia")),
 ]),
 dict(t="Tu HUD, parte por parte", icon="debug", lineas=[
  L("Ahora mira tu pantalla, porque el HUD de Horizon es totalmente nuevo.", None, [], ("hud", "todo")),
  L("Arriba en el centro está la brújula. Gira contigo y marca el norte, el sur, el este y el oeste.", "Arriba al centro: brújula", [], ("hud", "brujula")),
  L("Y justo debajo de la brújula está tu dinero: los billetes de tu alcancía, y abajo tus tickets.", "Debajo de la brújula: tu dinero", ["alcancia", "ticket"], ("hud", "dinero")),
  L("Arriba a la izquierda tienes tus coordenadas, hacia dónde miras, el bioma, la distancia a tu casa y tus misiones del día.", "Izquierda: coordenadas, bioma, casa y misiones", [], ("hud", "izq")),
  L("Arriba a la derecha está el radar redondo. Los puntos rojos son monstruos, los verdes animales y los celestes jugadores, hasta 24 bloques.", "Radar: rojo monstruos · verde animales · celeste jugadores", [], ("hud", "radar")),
  L("Y al lado del radar, el panel con el día, la hora, la luna, tus efectos y avisos, como la infección o el bloqueador.", "Derecha: día, hora, efectos y avisos", [], ("hud", "der")),
 ]),
 dict(t="La bola de calor", icon="bloqueador", lineas=[
  L("Abajo, en medio de tus corazones y tu comida, está la bola de calor. ¡Cambia de color según tu temperatura!", "Abajo al centro: la bola de calor", [], ("hud", "temp")),
  L("Azul oscuro: te estás congelando. Celeste: frío. Verde: perfecto. Naranja: calor. Y rojo: ¡te estás asando!", "Azul · celeste · verde · naranja · rojo", [], ("hud", "temp_ciclo")),
  L("Cada bioma tiene su temperatura. El desierto y el Nether calientan, la nieve y las montañas enfrían. Las antorchas, fogatas, hornos y la lava también te calientan.", "Biomas y fuego cambian tu calor", [], ("cuadro", 12), "brasas"),
  L("Si pasas de 82 grados te da hambre, y desde 92 náuseas y daño. Los bordes de la pantalla se ponen de fuego.", "82°: hambre · 92°: náuseas y daño", [], ("hud", "borde_calor"), "brasas"),
  L("Y si bajas de 10 grados, te congelas: escarcha en la pantalla, lentitud, debilidad y daño. ¡Corre a una fogata!", "Menos de 10°: te congelas", [], ("hud", "borde_frio"), "nieve"),
  L("Un truco: cualquier bloque encima de tu cabeza, aunque sea una losa, te cubre de la lluvia y del sol.", "Un bloque encima te cubre", [], ("big", '¡TECHO!', 'te cubre del sol y la lluvia', ['mc:planks_oak', 'mc:stone'])),
 ]),
 dict(t="Las gotas de sed", icon="hm_agua_hervida", lineas=[
  L("A la derecha, encima de la comida, están tus diez gotas de sed. Se van vaciando de izquierda a derecha.", "10 gotas de sed", [], ("hud", "sed")),
  L("Cuando te queda poca agua, las gotas parpadean en rojo. ¡Es tu aviso para beber!", "Poca agua: parpadean en rojo", [], ("hud", "sed_urge")),
  L("Bebe una botella de agua, una poción de agua o miel. O agáchate dentro del agua: así bebes y además te refrescas.", "Bebe, o agáchate en el agua", ["hm_agua_hervida"], ("hud", "sed_llenar"), "burbujas"),
  L("Sin agua te da lentitud, fatiga y daño. ¡No la descuides!", "Sin agua: lentitud y daño", [], ("big", 'SIN AGUA', 'lentitud · fatiga · daño', ['mc:potion_bottle_empty'])),
  L("Y ojo con el fuego: es infinito. No lo apaga el agua ni la lluvia, solo una poción arrojadiza de agua.", "Fuego infinito: solo poción arrojadiza", [], ("big", 'FUEGO ∞', 'solo una poción arrojadiza de agua', ['mc:campfire_log_lit', 'mc:potion_bottle_splash']), "brasas"),
 ]),
 dict(t="Infección zombi", icon="pastilla", lineas=[
  L("Si un zombi, un husk, un ahogado o un aldeano zombi te golpea, empiezas a sangrar y te infectas.", "Golpe zombi = sangrado + infección", [], ("cuadro", 13), "sangre"),
  L("En el panel derecho aparece un reloj: tienes cinco minutos antes de convertirte en zombi.", "¡5 minutos para curarte!", [], ("big", '5:00', 'antes de volverte zombi', ['mc:egg_zombie', 'mc:egg_husk', 'mc:egg_drowned']), "temblor"),
  L("El sangrado se detiene comiendo. Y la infección se cura con la pastilla antizombie: manzana dorada más cristal.", "Pastilla antizombie", ["pastilla"], ("receta", ["", "", "", "", "Manzana dorada", "Cristal", "", "", ""], "pastilla")),
  L("¡Y hay que terminar de comerla! En el próximo episodio: la vida diaria y las reglas del mundo. ¡Nos vemos!", None, [], ("items", ["pastilla"])),
 ]),
]),
# ════════════════════════════════════════════ 2
dict(n=2, titulo="Vida diaria y reglas", sub="Agua limpia, misiones, tu casa y las reglas de desafío", escenas=[
 dict(t="Vida diaria", icon="hm_cantimplora", lineas=[
  L("¡Hola de nuevo! Hoy te cuento cómo es el día a día en Horizon.", None, [], ("cuadro", 12)),
  L("El agua del río y las botellas normales no están hervidas: a veces te duele la panza. Mete la botella al horno o a una fogata.", "Hierve el agua: horno o fogata", ["hm_agua_hervida"], ("items", ["mc:potion_bottle_empty", "mc:furnace_front_on", "mc:campfire_log_lit", "hm_agua_hervida"])),
  L("La cantimplora guarda cinco tragos. Se hace con cuero, hilo y una botella. Llénala en un caldero con fuego abajo o bajo la lluvia para tener agua limpia.", "Cantimplora: 5 tragos", ["hm_cantimplora"], ("receta", ["", "Hilo", "", "Cuero", "Botella", "Cuero", "", "Cuero", ""], "hm_cantimplora")),
  L("La venda, de lana y papel, para el sangrado y cura corazón y medio. El botiquín te deja la vida completa, pero quédate quieta tres segundos.", "Venda y botiquín", ["hm_venda", "hm_botiquin"], ("receta", ["", "Cuero", "", "hm_venda", "Manzana dorada", "hm_venda", "", "Cuero", ""], "hm_botiquin")),
  L("Cada noche sin dormir cuenta: con tres o más estás cansada, lenta y pegas menos. Y mucho tiempo a oscuras da miedo: oyes pasos y susurros.", "Sin dormir: cansancio · oscuridad: miedo", [], ("big", '3 NOCHES', 'sin dormir = cansancio', ['mc:bed_red'])),
  L("Si mueres, tus cosas quedan en una tumba: un cofre con una valla y una cabeza encima. El chat te dice dónde.", "Al morir: tumba con tus cosas", [], ("big", 'TUMBA', 'tus cosas te esperan en la tumba', ['mc:chest_front'])),
 ]),
 dict(t="Misiones diarias", icon="libro", lineas=[
  L("¡Algo nuevo! Cada día de Minecraft recibes tres misiones: talar troncos, picar piedra, cazar zombis, caminar, pescar...", "3 misiones nuevas cada día", [], ("hud", "izq")),
  L("Las ves en el panel izquierdo, y al cumplir una se cobra sola: experiencia y billetes grises.", "Premio: experiencia + billetes grises", ["ficha"], ("items", ["ficha", "ficha", "ficha"]), "confeti"),
  L("Con /misiones ves tu progreso, y puedes cambiar una misión al día si no te gusta.", "/misiones: cambia una al día", [], ("cmd", "/misiones")),
 ]),
 dict(t="Faro de casa", icon="blk:hm_faro_lado", lineas=[
  L("Para no perderte, fabrica un Faro de casa: tablones en las esquinas, antorchas a los lados y un farol en el centro.", "Faro de casa", [], ("receta", ["Tablones", "Antorcha", "Tablones", "Antorcha", "Farol", "Antorcha", "Tablones", "Antorcha", "Tablones"], "~Faro")),
  L("Ponlo en tu casa y aparecerá un símbolo en la brújula, y en el panel izquierdo la distancia. ¡Además los meteoritos no caen cerca de él!", "Marca tu casa en la brújula", [], ("hud", "brujula_casa")),
 ]),
 dict(t="Reglas de desafío", icon="visualizador", lineas=[
  L("Ahora, las reglas que hacen a Horizon tan difícil.", None, [], ("cuadro", 21)),
  L("La redstone no existe: no se consigue, no se fabrica y no se coloca. Nada de pistones, repetidores, brújulas ni relojes.", "Sin redstone", [], ("big", 'SIN REDSTONE', 'ni pistones, ni repetidores, ni relojes', ['mc:redstone_dust', 'mc:repeater', 'mc:clock_item', 'mc:compass_item'])),
  L("De día, a cielo abierto, el sol te quema. El bloqueador solar te protege diez minutos, y puedes ponérselo a otro jugador.", "El sol quema: bloqueador 10 min", ["bloqueador"], ("big", '10:00', 'con bloqueador solar', ['bloqueador']), "brasas"),
  L("La caída hace el triple de daño, el fuego el doble, y la lava te mata al instante.", "Caída x3 · fuego x2 · lava mortal", [], ("big", 'x3', 'daño de caída', ['mc:campfire_log_lit', 'mc:bucket_lava']), "temblor"),
  L("Además no hay encantamiento de saqueo, las puertas y botones hacen un poquito de daño, al morir sueltas tu cabeza, y si alguien usa un tótem se avisa a todos.", "Sin saqueo · puertas dañan · sueltas tu cabeza", [], ("big", '¡CUIDADO!', 'hasta las puertas pican', ['mc:totem'])),
  L("¡Así que mucho cuidado ahí afuera! En el próximo episodio: los mobs. ¡Chao!", None, [], ("items", ["bloqueador"])),
 ]),
]),
# ════════════════════════════════════════════ 3
dict(n=3, titulo="Mobs reforzados", sub="Monstruos, Pepe, armaduras y el End", escenas=[
 dict(t="Mobs reforzados", icon="mc:egg_zombie", lineas=[
  L("¡Hola! Hoy hablamos de los mobs, porque en Horizon todos son mucho más peligrosos.", None, [], ("cuadro", 14), "temblor"),
  L("Los esqueletos tienen poquita vida, pero son rapidísimos y te elevan por los aires si estás cerca.", "Esqueletos: rápidos y te elevan", [], ("big", '¡ARRIBA!', 'te elevan si estás cerca', ['mc:egg_skeleton', 'mc:arrow'])),
  L("El creeper explota rápido y fuerte. Y uno de cada cinco es un creeper cargado, con aura azul: no te daña, ¡pero te lanza hasta 250 bloques al cielo!", "Creeper cargado: te lanza al cielo", [], ("big", '250', 'bloques hacia arriba', ['mc:egg_creeper']), "rayos"),
  L("Las arañas te ponen telaraña, y al romperla salen arañas de cueva. Cerca de los zombis te dan náuseas y hambre.", "Arañas: telaraña · zombis: náuseas", [], ("big", 'TELARAÑA', 'telaraña + arañas de cueva', ['mc:egg_spider', 'mc:web'])),
  L("El ghast se teletransporta y aguanta doce flechas. El breeze te ciega, la bruja te lanza efectos, y los vex te roban objetos.", "Ghast, breeze, bruja y vex", [], ("big", '12', 'flechas para el ghast', ['mc:egg_ghast', 'mc:arrow'])),
  L("Los phantoms te desordenan la barra de objetos. ¡Y el cubo de magma te mata de un golpe!", "¡Cubo de magma = muerte!", ["magma_eterno"], ("big", '¡MUERTE!', 'cubo de magma', ['mc:egg_magma_cube']), "temblor"),
  L("Y no puedes domar lobos, gatos, loros ni ocelotes. Los gólems y lobos se enfurecen si te acercas.", "No se pueden domar mascotas", [], ("big", 'SIN MASCOTAS', 'nada de mascotas', ['mc:egg_wolf', 'mc:egg_cat', 'mc:egg_parrot'])),
 ]),
 dict(t="¡Cuidado con Pepe!", icon="mc:egg_creeper", lineas=[
  L("¡Y conoce a Pepe! Un creeper chiquito que sale a veces al romper pasto, helechos u hojas.", "Pepe: sale del pasto y las hojas", [], ("cuadro", 14)),
  L("Te persigue y explota en cuanto suena la mecha, pero no rompe bloques. Tiene solo un corazón: ¡pégale primero!", "Explota sin romper bloques · 1 corazón", [], ("big", '¡PEPE!', 'pégale antes de que explote', ['mc:egg_creeper', 'mc:tallgrass']), "temblor"),
 ]),
 dict(t="Armaduras", icon="kit_reparacion", lineas=[
  L("Para defenderte, cada armadura completa te da un poder especial.", None, [], ("cuadro", 16)),
  L("Cuero: saciedad. Malla: velocidad y resistencia. Cobre, hierro y oro: vida extra.", "Cuero, malla, cobre, hierro, oro", [], ("big", 'SET COMPLETO', 'cada material, un poder', ['mc:leather_chestplate', 'mc:chainmail_chestplate', 'mc:copper_chestplate', 'mc:iron_chestplate', 'mc:gold_chestplate'])),
  L("Diamante: mucha vida extra. Y netherita: muchísima vida, regeneración, resistencia y absorción.", "Diamante y netherita: ¡mucha vida!", [], ("big", '¡MUCHA VIDA!', 'netherita: lo máximo', ['mc:diamond_chestplate', 'mc:netherite_chestplate'])),
  L("Necesitas el set completo del mismo material. Y el kit de reparación arregla toda tu armadura de golpe.", "Kit de reparación", ["kit_reparacion"], ("items", ["kit_reparacion"])),
 ]),
 dict(t="El End y el magma", icon="magma_eterno", lineas=[
  L("En el End viven los penantes: phantoms que te agarran y te suben. Solo te sueltan si los matas, ¡y caes sin protección!", "Penantes: te agarran y te suben", [], ("cuadro", 15)),
  L("También hay endermites en el suelo y ghasts en el aire, y el dragón lanza proyectiles de shulker y se regenera.", "Dragón más fuerte", [], ("big", 'DRAGÓN', 'proyectiles de shulker + regeneración', ['mc:egg_ender_dragon', 'mc:end_stone'])),
  L("Pisar un bloque de magma colocado te mata. Y para entrar al End necesitas el traje de endersita completo. Te lo explico en el episodio diez. ¡Hasta luego!", "Magma mata · End solo con endersita", ["endersita_casco"], ("items", ["endersita_casco", "endersita_peto", "endersita_pantalones", "endersita_botas"])),
 ]),
]),
# ════════════════════════════════════════════ 4
dict(n=4, titulo="Botín y objetos especiales", sub="Drops del cielo, carne podrida e ítems de Horizon", escenas=[
 dict(t="Drops del cielo", icon="ficha_verde", lineas=[
  L("¡Hola! Hoy toca conseguir cosas. Y en Horizon, ¡las cosas caen del cielo!", None, [], ("cuadro", 17), "estrellas"),
  L("Cada diez minutos cae un cofre cerca de ti, siempre en la superficie, con una columna de partículas para verlo de lejos. El chat te da las coordenadas.", "Cada 10 min cae un drop", [], ("big", '10:00', 'un cofre cae del cielo', ['mc:chest_front'])),
  L("¿Se te olvidó dónde cayó? Escribe /hm donde.", "/hm donde", [], ("cmd", "/hm donde")),
  L("Traen billetes grises, bloqueador, pastillas, carne, hilo, hierro, oro, carbón, flechas y agua.", "Billetes, pastillas, comida y más", ["ficha", "bloqueador", "pastilla"], ("items", ["ficha", "bloqueador", "pastilla", "mc:beef_raw", "mc:string", "mc:iron_ingot", "mc:coal", "mc:arrow"])),
  L("Además, los minerales se funden solos al romperlos, los animales sueltan el doble, y al talar el último tronco de un árbol, ¡caen manzanas de las hojas!", "Minerales fundidos · árboles dan manzanas", [], ("big", '¡MANZANAS!', 'tala el árbol completo', ['mc:log_oak', 'mc:apple', 'mc:apple_golden'])),
  L("Pero los animales de granja casi no aparecen: ¡cuida mucho los que tengas!", "Cuida a tus animales", [], ("big", '¡CUÍDALOS!', 'casi no aparecen', ['mc:egg_cow', 'mc:egg_pig', 'mc:egg_chicken', 'mc:egg_sheep'])),
 ]),
 dict(t="Carne podrida", icon="popo", lineas=[
  L("La carne y el pescado se pudren tras tres días de juego dentro de tu inventario. En su descripción ves la frescura.", "La carne se pudre en 3 días", [], ("cuadro", 18)),
  L("En un cofre el reloj se detiene. Y comer carne podrida tiene un cinco por ciento de volverte zombi. ¡Puaj!", "Guárdala en un cofre", [], ("big", '5%', 'de zombificarte', ['mc:rotten_flesh', 'mc:egg_zombie'])),
 ]),
 dict(t="Ítems especiales", icon="libro", lineas=[
  L("Horizon trae un montón de ítems nuevos. ¡Mira!", None, [], ("items", ["camara", "matrix", "visualizador", "debug", "gancho", "inventory"])),
  L("La lente de cámara cambia la vista. La Matrix muestra los chunks, y el Visualizador las hitboxes de los mobs, como en Java.", "Cámara, Matrix y Visualizador", ["camara", "matrix", "visualizador"], ("items", ["camara", "matrix", "visualizador"])),
  L("El ítem Debug muestra un panel tipo F3 arriba a la izquierda.", "Debug: panel tipo F3", ["debug"], ("hud", "debug")),
  L("El Inventory es de un solo uso: en tu próxima muerte conservas tus cosas y tu experiencia.", "Inventory: conservas tus cosas", ["inventory"], ("items", ["inventory"])),
  L("Y los divertidos: el 67 te da velocidad y salto, Love corazones, Angry un pájaro rojo que te da fuerza, Bro un corazón roto, y Triple T te disfraza de Tung Tung Sahur.", "67, Love, Angry, Bro y Triple T", ["item_67", "love", "angry", "bro", "triple_t"], ("items", ["item_67", "love", "angry", "bro", "triple_t"]), "corazones"),
  L("La espada de curación infernal hace ocho de daño extra y a veces te cura.", "Espada de curación infernal", ["espada_infernal"], ("receta", ["Espada netherita", "corazon_negro", "corazon_negro", "Vara de blaze", "Vara de blaze", "magma_eterno", "magma_eterno", "Cubeta de lava", ""], "espada_infernal")),
  L("Para los admins: varita de modo, brújula de teletransporte, interruptor Hardcore y capa de invisibilidad, con /hm admin.", "Admins: /hm admin", [], ("items", ["admin_modo", "admin_tp", "admin_hardcore", "admin_invisible"])),
  L("En el próximo episodio: corazones, el mazo y el gancho. ¡Chao!", None, [], ("items", ["corazon_dorado"])),
 ]),
]),
# ════════════════════════════════════════════ 5
dict(n=5, titulo="Corazones, mazo y gancho", sub="Magma eterno, corazones y la Extra Live", escenas=[
 dict(t="El gancho", icon="gancho", lineas=[
  L("¡Hola! Empecemos con el gancho: apunta a un bloque, hasta cuarenta bloques, ¡y te jala en línea recta!", "Te jala hasta 40 bloques", ["gancho"], ("cuadro", 23)),
  L("Tiene cinco usos y al llegar no te hace daño de caída.", "5 usos · sin daño de caída", [], ("big", '5', 'usos por gancho', ['gancho'])),
 ]),
 dict(t="Mazo de restauración", icon="mazo_restauracion", lineas=[
  L("El mazo de restauración es infinito y repara cosas usando tu experiencia.", "Repara usando tu XP", ["mazo_restauracion"], ("cuadro", 24)),
  L("En la segunda mano repara tu ítem. En la mano principal, repara la armadura de quien mires, o la tuya.", "Repara ítems y armaduras", [], ("big", '1 XP = 2', 'de durabilidad', ['mazo_restauracion'])),
  L("Se hace con una maza, cuatro netheritas, dos magma eterno y dos corazones rojos.", "Receta del mazo", ["magma_eterno", "corazon_rojo"], ("receta", ["Maza", "Netherita", "Netherita", "Netherita", "Netherita", "magma_eterno", "magma_eterno", "corazon_rojo", "corazon_rojo"], "mazo_restauracion")),
 ]),
 dict(t="Magma eterno y corazones", icon="corazon_dorado", lineas=[
  L("El magma eterno sale de los cubos de magma. Pero si lo llevas encima, pierdes un corazón para siempre cada minuto.", "Magma eterno: -1 corazón por minuto", ["magma_eterno"], ("big", '-1 ♥ / min', 'si llevas magma eterno', ['magma_eterno']), "brasas"),
  L("Dos medios corazones rojos, de los piglins brutos, hacen un corazón rojo.", "2 medios = 1 corazón rojo", [], ("items", ["medio_corazon_rojo", "medio_corazon_rojo", "corazon_rojo"])),
  L("El corazón dorado te devuelve un corazón: una manzana dorada encantada rodeada de ocho corazones rojos.", "Corazón dorado: recupera 1", [], ("receta", ["corazon_rojo"] * 4 + ["Manzana encantada"] + ["corazon_rojo"] * 4, "corazon_dorado"), "corazones"),
  L("El corazón celeste te los devuelve todos: bloques de oro en las esquinas y corazones dorados en cruz.", "Corazón celeste: recupera todos", [], ("receta", ["Bloque de oro", "corazon_dorado", "Bloque de oro", "corazon_dorado", "", "corazon_dorado", "Bloque de oro", "corazon_dorado", "Bloque de oro"], "corazon_celeste")),
  L("Y el corazón negro te da un corazón extra para siempre: un corazón celeste con cuatro netheritas en cruz.", "Corazón negro: +1 corazón permanente", [], ("receta", ["", "Netherita", "", "Netherita", "corazon_celeste", "Netherita", "", "Netherita", ""], "corazon_negro"), "corazones"),
 ]),
 dict(t="Extra Live", icon="extra_live", lineas=[
  L("En modo Hardcore, la Extra Live es como un tótem: si mueres con ella, vuelves a tu punto de reaparición.", "Una vida extra en Hardcore", ["extra_live"], ("items", ["extra_live"]), "estrellas"),
  L("Se gana una vez, venciendo al guardián anciano, al breeze, al warden y al wither. Revisa con /hm desafio.", "Vence a 4 jefes", [], ("cmd", "/hm desafio")),
  L("¡En el próximo episodio: dinero! Nos vemos.", None, [], ("items", ["ficha_arcoiris"])),
 ]),
]),
# ════════════════════════════════════════════ 6
dict(n=6, titulo="Dinero y comercio", sub="Billetes, alcancía, subasta y aldeanos", escenas=[
 dict(t="Billetes", icon="ficha_arcoiris", lineas=[
  L("¡Hola! Hoy nos hacemos ricas. Horizon tiene su propio dinero: los billetes.", None, [], ("cuadro", 26), "confeti"),
  L("Hay siete colores, de menor a mayor: gris, verde, azul, morado, amarillo, rojo y arcoíris.", "7 colores de billete", [], ("items", ["ficha", "ficha_verde", "ficha_azul", "ficha_morada", "ficha_amarilla", "ficha_roja", "ficha_arcoiris"])),
  L("Cuando juntas sesenta y cinco de un color, se convierten solos en uno del siguiente.", "65 de un color = 1 del siguiente", [], ("big", '65 → 1', 'se suben de color solos', ['ficha', 'ficha_verde'])),
 ]),
 dict(t="Alcancía", icon="alcancia", lineas=[
  L("Guarda tu dinero en la alcancía: cuatro bolas de arcilla y un tinte rosa. También hay Bonita, Copa, Pepa y Tralalelo.", "4 arcilla + tinte", [], ("items", ["alcancia", "alcancia_bonita", "alcancia_copa", "alcancia_pepa", "alcancia_tralalelo"])),
  L("Clic derecho guarda todos tus billetes, y agachada los sacas. Tu total aparece arriba, justo debajo de la brújula.", "Tu total: debajo de la brújula", [], ("hud", "dinero")),
  L("También puedes usar /depositar, /retirar y /alcancia.", "/depositar · /retirar · /alcancia", [], ("cmd", "/depositar todo")),
 ]),
 dict(t="La subasta", icon="bambu_infinito", lineas=[
  L("Cada treinta minutos, si hay dos o más jugadores, se subasta un premio: común, raro, épico o legendario.", "Subasta cada 30 min", [], ("cuadro", 19)),
  L("Puja con /sub y el código: por ejemplo, /sub g6 son seis billetes grises. O /asub para ganarle al líder por uno.", "/sub g6 · /asub", [], ("cmd", "/sub g6")),
  L("Los premios van desde pociones hasta el escudo infinito, el bambú infinito, la espada ignia... ¡y hasta popo, que no sirve para nada!", "Escudo infinito, bambú infinito...", [], ("items", ["bambu_infinito", "popo"])),
 ]),
 dict(t="Comercio con aldeanos", icon="ticket", lineas=[
  L("Los aldeanos no aceptan billetes: piden tickets, que viven en tu banco de tradeo.", "Los aldeanos piden tickets", ["ticket"], ("cuadro", 28)),
  L("El aldeano vestido de verde cambia tus billetes por tickets: doce grises dan un ticket.", "Aldeano verde: 12 grises = 1 ticket", [], ("big", '12 → 1', 'billetes grises → ticket', ['ficha', 'ticket'])),
  L("Toca a un aldeano con oficio, elige una oferta, y listo. Suben de nivel con tus compras y venden cosas mejores.", "Toca un aldeano y compra", [], ("items", ["pastilla", "bloqueador", "kit_reparacion", "gancho", "matrix", "item_67"])),
  L("Y el comerciante errante trae rarezas: Love, Angry, Bro, Triple T, ¡y a veces élitros! Nos vemos en el próximo.", "Comerciante errante: rarezas", [], ("items", ["love", "angry", "bro", "triple_t"])),
 ]),
]),
# ════════════════════════════════════════════ 7
dict(n=7, titulo="Clanes, intercambios y bodas", sub="Juega en comunidad", escenas=[
 dict(t="Clanes", icon="corazon_rojo", lineas=[
  L("¡Hola! Horizon se juega mejor con amigos. ¡Hablemos de clanes!", None, [], ("cuadro", 29)),
  L("Crea tu clan con /createc y el nombre, y serás el Líder. Hasta cincuenta miembros.", "/createc Nombre · hasta 50", [], ("cmd", "/createc Estrellitas")),
  L("Con /joinc pides entrar, con /exitc te sales, y con /c gestionas tu clan.", "/joinc · /exitc · /c", [], ("cmd", "/joinc")),
  L("Hay rangos: Miembro, Moderador, Sublíder y Líder. Con /mgc hablas solo con tu clan, y el Líder puede pujar con el dinero del clan.", "Rangos · chat · dinero del clan", [], ("big", 'LÍDER', 'Sublíder · Moderador · Miembro', ['corazon_rojo'])),
 ]),
 dict(t="Intercambio seguro", icon="ficha_amarilla", lineas=[
  L("Para intercambiar sin trampas, escribe /trade y el nombre del otro jugador.", "/trade Nombre", [], ("cuadro", 30)),
  L("Hasta seis ítems y los billetes que quieras. Los dos confirman, y si alguien cambia algo, se quitan las confirmaciones. ¡Nadie se lleva sorpresas!", "Los dos confirman", [], ("big", '✔ ✔', 'o se hace completo, o no se hace', ['ficha_amarilla', 'mc:emerald'])),
 ]),
 dict(t="Bodas y parejas", icon="anillo_boda", lineas=[
  L("¡Y en Horizon te puedes casar! Fabrica un anillo de compromiso con un diamante y tres de oro, y haz clic en tu persona favorita.", "Anillo de compromiso", ["anillo_compromiso"], ("items", ["anillo_compromiso"]), "corazones"),
  L("Para la boda, cada uno necesita un anillo de boda, de esmeralda y oro, y un altar de bodas hecho con oro, amatista y cuarzo.", "Anillos de boda + altar", ["anillo_boda"], ("receta", ["Oro", "Amatista", "Oro", "Cuarzo", "Cuarzo", "Cuarzo", "Cuarzo", "Cuarzo", "Cuarzo"], "~Altar")),
  L("Suenan campanas, caen pétalos, dicen sus votos, ¡y fuegos artificiales y confeti!", "Campanas, pétalos y confeti", ["confeti", "ramo_novia"], ("items", ["ramo_novia", "confeti", "anillo_boda"]), "confeti"),
  L("Casados, cerca de tu pareja te curas solo, porque el amor cura. Agáchate muy cerca para darle un beso.", "El amor cura ♥", [], ("big", '♥ + ♥', 'cerca de tu pareja te curas', ['anillo_boda', 'anillo_boda']), "corazones"),
  L("Usa /pareja para ver su estado o ir con ella, y /mgp para su chat privado. ¡Qué romántico! Nos vemos.", "/pareja · /mgp", [], ("cmd", "/pareja")),
 ]),
]),
# ════════════════════════════════════════════ 8
dict(n=8, titulo="Tu casa: bolsitas, cuadros y muebles", sub="Guarda tus cosas y decora", escenas=[
 dict(t="Bolsitas", icon="bolsa_shulker", lineas=[
  L("¡Hola! Hoy toca organizar y decorar. Primero, las bolsitas.", None, [], ("cuadro", 20)),
  L("La bolsita guarda veintisiete pilas. Úsala y aparece flotando frente a ti; tócala y se abre como un cofre.", "27 pilas · flota frente a ti", [], ("items", ["bolsa_pink", "bolsa_blue", "bolsa_green", "bolsa_yellow", "bolsa_purple"])),
  L("Solo tú la puedes abrir. Se hace con una bolsa de cualquier color y un cofre. Y con un ojo de ender, sale la bolsita del End.", "Bolsa + cofre · bolsa + ojo de ender", ["bolsa_end"], ("items", ["bolsa_pink", "bolsa_end"])),
  L("Y la shulker reforzada tiene cincuenta y cuatro casillas, ¡y no la rompen ni explosiones ni lava!", "Shulker reforzada: 54 casillas", [], ("big", '54', 'casillas a prueba de todo', ['mc:purpur_block', 'mc:obsidian'])),
 ]),
 dict(t="Cuadros", icon="cuadro_azar", lineas=[
  L("Horizon tiene ciento treinta y seis cuadros de pixel art. ¡Incluso hay veinticuatro que explican el addon, como estos!", "136 cuadros de pixel art", [], ("cuadro", 12)),
  L("El ítem Cuadro sale de cualquier pintura y elige uno al azar que quepa en la pared.", "Cuadro al azar", ["cuadro_azar"], ("cuadro", 35)),
  L("Y los de dos por dos tienen su propio ítem: una pintura más un tinte, o más algo del tema. ¡El pastor también los vende!", "Pintura + tinte = cuadro", [], ("cuadro", 27)),
 ]),
 dict(t="Muebles", icon="blk:muebles/hm_mu_madera_roble", lineas=[
  L("Por último, los muebles: sillas, mesas, sofás, estanterías, lámparas y plantas.", "Sillas, mesas, sofás, lámparas...", [], ("big", 'MUEBLES', 'decora tu casa', ['blk:muebles/hm_mu_madera_roble', 'blk:muebles/hm_mu_tela_rosa', 'mc:lantern'])),
  L("Clic derecho en una silla o un sofá para sentarte, y agáchate para levantarte. Las lámparas se prenden con clic. ¡Nos vemos en el próximo!", "Clic: sentarte · agáchate: levantarte", [], ("big", '¡A DECORAR!', '', ['blk:muebles/hm_mu_madera_cerezo', 'blk:muebles/hm_mu_flores'])),
 ]),
]),
# ════════════════════════════════════════════ 9
dict(n=9, titulo="Clima, catástrofes y eventos", sub="Meteoritos, tormentas, Sol Muerto y Luna de Sangre", escenas=[
 dict(t="Catástrofes", icon="hm_hierro_meteorico", lineas=[
  L("¡Hola! Hoy toca la parte más intensa: ¡las catástrofes!", None, [], ("cuadro", 22), "temblor"),
  L("Más o menos cada día y medio empieza un evento. Lo ves en el panel derecho con el tiempo que le queda.", "Un evento cada día y medio", [], ("hud", "der")),
  L("En la lluvia de meteoritos caen rocas de fuego con minerales del espacio: hierro meteórico, olivino, troilita y, muy rara vez, lonsdaleíta.", "Meteoritos: minerales del espacio", [], ("items", ["hm_hierro_meteorico", "hm_olivino", "hm_troilita", "hm_lonsdaleita"]), "brasas"),
  L("Pero el cráter queda radiactivo dos días. Usa el traje antirradiación, y el dosímetro te dice dónde está el peligro.", "Traje antirradiación + dosímetro", [], ("items", ["hm_rad_mascara", "hm_rad_traje", "hm_rad_faldon", "hm_rad_botas", "hm_dosimetro"])),
  L("Hay tormentas de arena, ventiscas, y tormentas eléctricas donde los rayos buscan la armadura de metal.", "Arena · ventisca · rayos", [], ("big", '¡RAYOS!', 'los rayos buscan el metal', ['mc:iron_chestplate']), "rayos"),
  L("Y granizo, lluvia ácida, olas de calor y de frío, niebla con mobs escondidos ¡y terremotos que abren grietas con minerales!", "Granizo, ácido, niebla, terremotos", [], ("big", '¡TERREMOTO!', 'grietas con minerales', ['mc:stone', 'mc:iron_ore', 'mc:diamond_ore']), "temblor"),
 ]),
 dict(t="Luna de Sangre", icon="ecl_item_luna", fondo="eclipse", lineas=[
  L("Ahora, los dos eventos más temidos. Primero, la Luna de Sangre: cada noche tiene un diez por ciento de probabilidad.", "10% cada noche", [], ("big", '10%', 'cada noche', ['ecl_item_luna']), "sangre"),
  L("El cielo se pone rojo, llueve sangre y no puedes dormir. Los mobs hacen cinco veces más daño y tienen cinco veces más vida.", "Mobs x5 daño y x5 vida", [], ("big", 'x5', 'daño y vida', ['mc:egg_zombie', 'mc:egg_skeleton', 'mc:egg_creeper']), "sangre"),
 ]),
 dict(t="Sol Muerto", icon="ecl_item_eclipse", fondo="eclipse", lineas=[
  L("Y el Sol Muerto: en el panel derecho ves el día, de mil. Al llegar al día mil, el sol muere para siempre.", "Día 1000: el sol muere", [], ("cuadro", 22)),
  L("El cielo queda negro, y los mobs hacen el triple de daño y tienen el doble de vida. ¡Prepárate antes!", "Mobs x3 daño · x2 vida", [], ("big", '1000', 'días antes del fin', ['ecl_item_eclipse']), "temblor"),
  L("Pero no todo es malo: en noches despejadas salen auroras de colores. ¡Preciosas! Nos vemos en el próximo.", "Auroras en noches despejadas", [], ("big", 'AURORAS', 'verde · turquesa · morado · rosa', ['mc:nether_star']), "estrellas"),
 ]),
]),
# ════════════════════════════════════════════ 10
dict(n=10, titulo="Bajo el mar y al espacio", sub="Buceo, oxígeno, endersita y el Espacio", escenas=[
 dict(t="Buceo y oxígeno", icon="tanque_oxigeno", lineas=[
  L("¡Hola, exploradora! Hoy vamos a los extremos. Primero, el fondo del mar.", None, [], ("cuadro", 32), "burbujas"),
  L("Cada diez bloques de agua suman una atmósfera. A diez bloques gastas el aire el doble de rápido, a veinte el triple.", "Cada 10 bloques: +1 atm", [], ("big", '+1 atm', 'cada 10 bloques', ['mc:bucket_water', 'tanque_oxigeno']), "burbujas"),
  L("El tanque vacío se hace con cobre arriba, hierro y caucho en medio, y hierro abajo.", "Tanque de oxígeno", [], ("receta", ["", "Cobre", "", "Hierro", "caucho", "Hierro", "Hierro", "Hierro", "Hierro"], "tanque_vacio")),
  L("El oxígeno sale de electrólisis más un cubo de agua, como en Dr. Stone. Llena el tanque y póntelo en el pecho.", "Electrólisis + agua = oxígeno", [], ("items", ["electrolisis", "oxigeno", "tanque_oxigeno"]), "burbujas"),
 ]),
 dict(t="Endersita: el traje espacial", icon="endersita_casco", lineas=[
  L("Ahora la endersita, el traje espacial. Con el set completo sumas cincuenta corazones y tienes oxígeno sin límite.", "+50 corazones · oxígeno infinito", [], ("cuadro", 31), "estrellas"),
  L("Cada pieza lleva caucho, aislante, magma eterno, una pieza mix y tres de kevlar.", "Receta de cada pieza", [], ("receta", ["caucho", "aislante_termico", "caucho", "magma_eterno", "mix_peto", "magma_eterno", "kevlar", "kevlar", "kevlar"], "endersita_peto")),
  L("El caucho sale del látex de los troncos pelados. El aislante, de nueve kapton de los cubos de magma.", "Látex → caucho · kapton → aislante", [], ("items", ["latex_natural", "caucho", "kapton", "aislante_termico"])),
  L("La pieza mix junta las siete del mismo tipo, de cuero a netherita. Y el kevlar lleva carbono, cloro, nitrógeno, azufre y agua.", "Mix y kevlar", [], ("items", ["mix_casco", "carbono_aromatico", "cloro_puro", "nitrogeno", "kevlar"])),
 ]),
 dict(t="El Espacio", icon="endersita_casco", fondo="espacio", lineas=[
  L("¿Y el Espacio? Sube hasta la altura doscientos ochenta y entras: cielo negro, estrellas, un planeta y la Luna.", "Desde Y 280: el Espacio", [], ("cuadro", 35), "estrellas"),
  L("Saltas altísimo y caes despacio. Pero sin traje, el vacío te aplasta y solo aguantas la respiración quince segundos.", "Sin traje: el vacío te aplasta", [], ("big", '15 s', 'de aire sin traje', ['endersita_casco'])),
  L("¡Qué aventura! En el último episodio: pesca, minijuegos y comandos.", None, [], ("items", ["endersita_casco"])),
 ]),
]),
# ════════════════════════════════════════════ 11
dict(n=11, titulo="Pesca, minijuegos y comandos", sub="Diversión y resumen final", escenas=[
 dict(t="Pesca", icon="hm_pez_carpa", lineas=[
  L("¡Hola! Llegamos al último episodio. Empecemos tranquilas: ¡a pescar!", None, [], ("items", ["hm_pez_carpa", "hm_pez_trucha", "hm_pez_atun"]), "burbujas"),
  L("Lanza la caña. Cuando salgan los signos de exclamación, toca la caña rápido.", "Cuando salga ¡! toca la caña", [], ("big", '¡!', '¡toca la caña!', ['mc:fishing_rod_uncast'])),
  L("Mantén agacharte para subir la barra verde, y suelta para bajarla. Mantén al pez dentro hasta llenar la captura.", "Pez dentro de la barra verde", [], ("big", '¡ATRÁPALO!', 'mantenlo en la barra', ['hm_pez_carpa'])),
  L("Hay dieciocho especies, cada una en su lugar y a su hora, como el Pez Leyenda. Míralas con /pesca.", "18 especies · /pesca", [], ("items", ["hm_pez_pulpo", "hm_pez_esturion", "hm_pez_pirana", "hm_pez_leyenda"])),
 ]),
 dict(t="Minijuegos", icon="resortera", lineas=[
  L("Cada cierto tiempo se anuncia un minijuego. Escribe /participo para entrar, y /minisalir para volver con todas tus cosas.", "/participo · /minisalir", [], ("cmd", "/participo")),
  L("Hay HorizonWare, salta la cuerda, cruza la calle, la viborita, barriles, lanzapájaros y defensa de núcleos.", "¡Un montón de minijuegos!", [], ("cuadro", 33)),
  L("Y la guerrita de pintura: rojos contra azules. Cada eliminación te sube de arma, ¡y gana quien elimine con la Raypaint!", "Guerrita de pintura", [], ("cuadro", 34), "confeti"),
  L("El primer lugar gana cuarenta billetes verdes, el segundo veinte y el tercero diez.", "Premios: 40 · 20 · 10 verdes", [], ("big", '40 · 20 · 10', 'billetes verdes', ['ficha_verde'])),
 ]),
 dict(t="Comandos útiles", icon="camara", lineas=[
  L("Para terminar, los comandos más útiles. Con /guia abres el libro, y /misiones tus misiones.", "/guia · /misiones", [], ("cmd", "/guia")),
  L("/hm donde te dice dónde cayó tu drop, y /hm ligero quita partículas si tu juego va lento.", "/hm donde · /hm ligero", [], ("cmd", "/hm ligero")),
  L("Para el dinero, /sub y /alcancia. Para clanes, /createc. Para intercambiar, /trade. Y para tu pareja, /pareja.", "/sub · /createc · /trade · /pareja", [], ("cmd", "/trade")),
  L("¡Y eso es todo! Ya sabes todo para sobrevivir en Horizon. Gracias por ver la serie, ¡y mucha suerte!", None, [], ("big", '¡GRACIAS!', 'con cariño, Yei ♥', ['libro']), "confeti"),
 ]),
]),
]
