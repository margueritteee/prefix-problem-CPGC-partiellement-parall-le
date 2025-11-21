from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder='interface', static_folder='interface')


def parallel_prefix_sum_prof(x): 
    n = len(x)
    if n == 0: # ida x fargha return 3 tables vide
        return [], [], []

    # Somme parallèle (nfs el algo li gblha (partiellement parallèle))
    arbre_somme = [x.copy()] 
    niveau_courant = x.copy() 
    while len(niveau_courant) > 1:
        niveau_suivant = []
        for i in range(0, len(niveau_courant), 2):
            if i + 1 < len(niveau_courant):
                niveau_suivant.append(niveau_courant[i] + niveau_courant[i + 1])
            else:
                niveau_suivant.append(niveau_courant[i])
        arbre_somme.append(niveau_suivant)
        niveau_courant = niveau_suivant

    # Calcule préfixe
    somme_prefixe = [0] * n  # tableau final des sommes préfixes

    if n == 1:
        somme_prefixe[0] = x[0]  # si un seul élément la somme prefixe hya nfsha
    else:
        sommes_paires = [0] * ((n + 1) // 2)  #ida kayn aktr mn element , on cree table sommes_paires w nstocko les elements 2 b 2 
        #exmple :x = [1, 2, 3, 4] n=4 meanaha pair (n + 1)//2 = (4+1)//2 = 5//2 = 2 => aendna 2 paires [1+2][3+4]
        #x = [1, 2, 3, 4, 5] => n = 5 (impair) , (n + 1)//2 = (5+1)//2 = 6//2 = 3 => aendna 3 paires [1+2][3+4][5]
        # Construction des sommes par paire
        for i in range(len(sommes_paires)): #parcours kaml sommes_paires 
            if 2*i + 1 < n:  # i les indices dans x , verifie juste que la paire est complète 
                sommes_paires[i] = x[2*i] + x[2*i + 1] #tdi les elements motatlya w tjm3hm laztm t799 que paire complete , example Si x = [1,2,3,4] => n = 4 
                #i = 0 => 2*i + 1 = 1 < 4 paire complete [1,2] / i = 1 => 2*i + 1 = 3 < 4 paire complete[3,4]
                #x = [1,2,3,4] i = 0 => x[0] + x[1] = 1 + 2 = 3 => sommes_paires[0] = 3
                #i = 1 => x[2] + x[3] = 3 + 4 = 7 => sommes_paires[1] = 7
            else:  # dernier élément seul si n impair
                sommes_paires[i] = x[2*i] #x = [1, 2, 3, 4, 5] => n = 5 / i=2 5<5 (no) => 2*i = 4 donc x[4] = 5 , sommes_paires = [3, 7, 5]

        # Calcul du prefix sum de ces paires
        prefix_paires = [0] * len(sommes_paires) #stocker les sommes préfixes des paires kaml 0 
        prefix_paires[0] = sommes_paires[0] #awl element fel somme_paire howa awl element fel prefix
        for i in range(1, len(sommes_paires)):
            prefix_paires[i] = prefix_paires[i-1] + sommes_paires[i] #mtln: sommes_paires = [3, 7, 5] prefix_paires[i]=[3,(3+7=)10,(10+5=)15]

        #somme_prefixe final
        for i in range(n): #parcourt tous les indices du tableau x
            if i == 0: #awl element yb9a nfso ntae x
                somme_prefixe[i] = x[0]
            elif (i + 1) % 2 == 0:  # indice pair (base1)
                somme_prefixe[i] = prefix_paires[(i + 1)//2 - 1] #Exemple:x = [1,2,3,4,5] , sommes_paires = [1+2, 3+4, 5] = [3, 7, 5] , prefix_paires = [3, 10, 15] 
                #i = 1=> (i+1)//2 - 1 = (2)//2 - 1 = 1 - 1 = 0,somme_prefixe[1] = prefix_paires[0] = 3 
            else:  # indices impairs 
                somme_prefixe[i] = prefix_paires[i//2 - 1] + x[i] #Pour i = 2 (3ème élément, x[2]=3) => somme_prefixe[2] = prefix_paires[0] + x[2] = 3 + 3 = 6

    # arbre le meme avec (partiellement parallèle)
    arbre_recon = [somme_prefixe.copy()]
    niveau_courant = somme_prefixe.copy()
    while len(niveau_courant) > 1:
        niveau_suivant = []
        for i in range(0, len(niveau_courant), 2):
            if i + 1 < len(niveau_courant):
                niveau_suivant.append(niveau_courant[i + 1])
            else:
                niveau_suivant.append(niveau_courant[i])
        arbre_recon.append(niveau_suivant)
        niveau_courant = niveau_suivant

    return somme_prefixe, arbre_somme, arbre_recon


@app.route("/", methods=["GET", "POST"])
def index():
    input_numbers = ""
    somme_prefixe_resultat = []
    arbre_somme = []
    arbre_recon = []

    if request.method == "POST":
        input_numbers = request.form.get("numbers", "")
        try:
            numbers = [int(num.strip()) for num in input_numbers.split(",")]
            somme_prefixe_resultat, arbre_somme, arbre_recon = parallel_prefix_sum_prof(numbers)
        except ValueError:
            somme_prefixe_resultat = arbre_somme = arbre_recon = ["Erreur : entrez des nombres séparés par des virgules"]

    return render_template("index.html",
                           input_numbers=input_numbers,
                           S=somme_prefixe_resultat,
                           up_tree=arbre_somme,
                           down_tree=arbre_recon)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
