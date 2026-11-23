// Rubrique « Évaluation » : déchiffre, dans le navigateur, les notes de
// l'élève à partir de son prénom et de son code personnel. Le fichier
// notes.json est produit par scripts/notes_snt.py ; la dérivation de clé
// et la normalisation du prénom doivent rester identiques des deux côtés.
(function () {
  'use strict';

  const form = document.getElementById('eval-form');
  if (!form) return;
  const message = document.getElementById('eval-message');
  const resultat = document.getElementById('eval-resultat');
  const bouton = form.querySelector('button');
  let donnees = null;

  function normaliserPrenom(prenom) {
    return prenom.normalize('NFD').replace(/[̀-ͯ]/g, '')
      .toLowerCase().replace(/[^a-z]/g, '');
  }

  function normaliserCode(texte) {
    return texte.toUpperCase().replace(/[^A-Z0-9]/g, '');
  }

  function base64(texte) {
    return Uint8Array.from(atob(texte), (c) => c.charCodeAt(0));
  }

  function hex(octets) {
    return Array.from(octets, (o) => o.toString(16).padStart(2, '0')).join('');
  }

  function afficherMessage(texte, erreur) {
    message.textContent = texte;
    message.classList.toggle('text-danger', Boolean(erreur));
  }

  function formaterNote(valeur) {
    if (valeur === null || valeur === undefined) return '—';
    if (valeur === 'ABS') return 'Absent';
    return String(valeur).replace('.', ',');
  }

  async function chargerDonnees() {
    if (donnees) return donnees;
    const reponse = await fetch('notes.json', { cache: 'no-cache' });
    if (!reponse.ok) throw new Error('notes indisponibles');
    donnees = await reponse.json();
    return donnees;
  }

  async function dechiffrer(prenom, code) {
    const d = await chargerDonnees();
    if (!Object.keys(d.entrees).length) throw new Error('aucune note publiée');
    const secret = new TextEncoder().encode(normaliserPrenom(prenom) + '|' + code);
    const base = await crypto.subtle.importKey('raw', secret, 'PBKDF2', false, ['deriveBits']);
    const bits = new Uint8Array(await crypto.subtle.deriveBits(
      { name: 'PBKDF2', hash: 'SHA-256', salt: base64(d.kdf.sel), iterations: d.kdf.iterations },
      base, 512));
    const ident = hex(bits.slice(32, 48));
    const entree = d.entrees[ident];
    if (!entree) return null;
    const cle = await crypto.subtle.importKey('raw', bits.slice(0, 32), 'AES-GCM', false, ['decrypt']);
    const clair = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: base64(entree.iv), additionalData: new TextEncoder().encode(ident) },
      cle, base64(entree.donnees));
    return JSON.parse(new TextDecoder().decode(clair));
  }

  function cellule(ligne, balise, texte) {
    const c = document.createElement(balise);
    c.textContent = texte;
    ligne.appendChild(c);
    return c;
  }

  function afficherNotes(eleve, miseAJour) {
    resultat.replaceChildren();
    const titre = document.createElement('h2');
    titre.textContent = eleve.prenom + ' ' + eleve.nom + ' — ' + eleve.classe;
    resultat.appendChild(titre);

    const table = document.createElement('table');
    table.className = 'table table-sm';
    const tete = table.createTHead().insertRow();
    ['Évaluation', 'Ta note /20', 'Moyenne de la classe'].forEach((t) => cellule(tete, 'th', t));
    const corps = table.createTBody();
    eleve.evaluations.forEach((e) => {
      const ligne = corps.insertRow();
      cellule(ligne, 'td', e.titre);
      cellule(ligne, 'td', formaterNote(e.note));
      cellule(ligne, 'td', formaterNote(e.moyenne_classe));
    });
    const pied = table.createTFoot().insertRow();
    cellule(pied, 'th', 'Moyenne');
    cellule(pied, 'th', formaterNote(eleve.moyenne));
    cellule(pied, 'th', '');
    resultat.appendChild(table);

    const note = document.createElement('p');
    note.className = 'small';
    note.textContent = 'Notes mises à jour le ' +
      new Date(miseAJour + 'T12:00:00').toLocaleDateString('fr-FR') +
      '. « — » : pas encore noté. En cas d\'erreur, parles-en à ton professeur.';
    resultat.appendChild(note);
  }

  form.addEventListener('submit', async (evenement) => {
    evenement.preventDefault();
    resultat.replaceChildren();
    const prenom = form.elements.prenom.value;
    const code = normaliserCode(form.elements.code.value);
    if (!normaliserPrenom(prenom) || code.length !== 8) {
      afficherMessage('Indique ton prénom et ton code personnel de 8 caractères.', true);
      return;
    }
    if (!window.crypto || !crypto.subtle) {
      afficherMessage('Ce navigateur ne permet pas d\'afficher les notes.', true);
      return;
    }
    bouton.disabled = true;
    afficherMessage('Recherche en cours…', false);
    try {
      const eleve = await dechiffrer(prenom, code);
      if (!eleve) {
        afficherMessage('Prénom ou code incorrect.', true);
      } else {
        afficherMessage('', false);
        afficherNotes(eleve, donnees.mise_a_jour);
        form.elements.code.value = '';
      }
    } catch (erreur) {
      afficherMessage('Les notes ne sont pas disponibles pour le moment.', true);
    } finally {
      bouton.disabled = false;
    }
  });
})();
