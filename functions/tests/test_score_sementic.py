import unittest
from unittest.mock import patch, MagicMock
import numpy as np


from functions import score_sementic

class TestPertinenceSementicFunction(unittest.TestCase):

    def test_pertinence_sementic(self):

        # Un modèle léger de SBERT
        similarity_mot_recherche_1 = 0.2695721983909607
        similarity_mot_recherche_2 = 0.17542529106140137
        similarity_mot_analyse_1 = 0.46018004417419434
        similarity_mot_analyse_2 = 0.11271010339260101

        # Un modèle fasttext
        #similarity_mot_recherche_1 = 0.55825204
        #similarity_mot_recherche_2 = 0.5113726
        #similarity_mot_analyse_1 = 0.4894558
        #similarity_mot_analyse_2 = 0.6316683
        
        mean_similarity_score = np.mean([similarity_mot_recherche_1, similarity_mot_recherche_2, 
                                         similarity_mot_analyse_1, similarity_mot_analyse_2])
        print(mean_similarity_score)

        mot_recherche_1 = "merveilleux"
        mot_recherche_2 = "été"
        mot_analyse_1 = "village"
        mot_analyse_2 = "temps"
        cleaned_text = "Un matin ensoleillé, dans le village tranquille de Montclar, les habitants se levaient tous avec une énergie nouvelle. La saison de l'été était arrivée, et avec elle, une fraîcheur qui remplissait les rues étroites et les maisons aux toits de tuiles rouges. Montclar, petit village situé dans les montagnes, était un endroit où les journées passaient doucement, sans hâte, et où les gens prenaient le temps de se saluer, de s'entraider et de discuter des événements de la journée. Les enfants couraient dans les ruelles, leurs rires résonnant dans l'air frais, tandis que les adultes se réunissaient sur la place du marché pour échanger les dernières nouvelles. C'était un endroit où la nature dictait le rythme de la vie. Les habitants cultivaient leurs jardins et s'occupaient des champs autour du village. La mer était loin, mais l'air était si pur qu'il semblait presque enivrant. Les montagnes majestueuses entouraient le village, formant une barrière naturelle contre le monde extérieur. À chaque saison, le paysage se transformait : au printemps, les fleurs colorées éclosent sur les pentes, l'été apportait une chaleur douce, l'automne peignait les arbres de couleurs flamboyantes, et l'hiver recouvrait le village de neige, transformant Montclar en un véritable paradis hivernal. Dans ce cadre idyllique, les habitants de Montclar avaient appris à apprécier la simplicité de la vie. Ils ne se laissaient pas troubler par les bruits du monde moderne. Les réseaux sociaux n'étaient pas leur priorité, et la télévision restait souvent éteinte. Ils prenaient plaisir à la conversation, à la marche dans les collines et à la contemplation des étoiles la nuit. Le ciel était d'une clarté rare, loin de la pollution des grandes villes. Chaque soir, en levant les yeux, on pouvait observer des constellations brillantes qui semblaient veiller sur eux. Il y avait un café, le 'Café du Soleil', où tous les habitants se retrouvaient le matin pour échanger des nouvelles et discuter de la vie quotidienne. Le vieux Maurice, le propriétaire, servait toujours un café chaud avec un sourire sincère. Il avait vu des générations d'enfants grandir, et chaque matin, il racontait des histoires du passé aux jeunes qui venaient écouter. Ses yeux pétillaient chaque fois qu'il évoquait les anciens temps, quand le village était encore plus isolé et que les gens se rendaient à pied au marché le plus proche, à des heures de marche. Là-bas, dans le café, on sentait la chaleur humaine et la bienveillance qui régnaient entre les habitants. Les discussions allaient de la météo à la récolte de l'année, en passant par les dernières anecdotes sur les animaux du village ou les dernières blagues de l'été. Ce n'était pas un lieu où les gens venaient pour être seuls ou pour rester dans leur monde intérieur. Au contraire, c'était un lieu de partage, un endroit où chacun pouvait s'exprimer et où l'on s'écoutait véritablement. Au fur et à mesure des semaines, la vie à Montclar suivait son cours paisible. Les saisons changeaient, et avec elles, les préoccupations des villageois. Les récoltes arrivaient à terme, les jardins étaient entretenus, et le cycle des fêtes locales continuait. Le village était un endroit où l'on célébrait les petites victoires de la vie quotidienne. Les habitants se retrouvaient pour des fêtes simples mais joyeuses, où la nourriture maison et les danses traditionnelles occupaient une place de choix. Tout cela faisait partie de la richesse de la vie à Montclar, et c'est cette simplicité qui rendait ce village si spécial. Malgré la tranquillité qui régnait, la vie à Montclar n'était pas toujours aussi calme qu'elle en avait l'air. Les habitants avaient parfois des conflits, comme partout ailleurs, mais ceux-ci étaient rapidement résolus, souvent avec un peu de sagesse et beaucoup de dialogue. Il n'était pas rare qu'un villageois passe chez un autre pour discuter d'un désaccord ou pour demander un conseil. C'était une communauté où l'entraide était naturelle et où l'on se souciait du bien-être de ses voisins. Dans ce cadre, il était facile de se sentir en sécurité et entouré de gens bienveillants. Les vacances d'été approchaient, et les enfants se préparaient à quitter l'école pour quelques semaines de liberté. L'excitation montait parmi eux, et tous avaient hâte de pouvoir courir dans les champs, explorer les montagnes et s'amuser sous le soleil. Les parents, quant à eux, étaient plus concentrés sur les tâches quotidiennes, mais chacun attendait ce moment de l'année avec impatience, car l'été apportait une légèreté particulière. Les longues journées étaient idéales pour des promenades dans la nature, des pique-niques au bord de la rivière, ou des siestes à l'ombre des grands chênes. La douceur de l'été à Montclar était quelque chose de rare, un cadeau que l'on savourait pleinement. Dans ce coin du monde, loin des préoccupations et du stress des grandes villes, on appréciait les choses simples. On vivait au rythme des saisons, avec la conviction que le monde était encore un endroit merveilleux, à condition de savoir y prêter attention."


        similarity_score, score = score_sementic.pertinence_sementic(cleaned_text, mot_recherche_1, mot_recherche_2,
                                                                        mot_analyse_1, mot_analyse_2)
        print ([similarity_score, score])
        self.assertAlmostEqual(mean_similarity_score, score, places=1)

if __name__ == '__main__':
    unittest.main()