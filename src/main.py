#!/usr/bin/env python3

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
QLabel, QComboBox, QPushButton, QLineEdit, QSpinBox, QPlainTextEdit,
QMessageBox, QInputDialog)
from PyQt5 import QtCore
from collections import OrderedDict
import re

from lib.ranked_pairs import RankedPairs
from lib.stv import STV
from lib.exceptions import InvalidTieBreakerException, InvalidBallotException, TooManyBlankBallotsException, TieBreakerNeededException

current_election_type = None
election_types = OrderedDict(sorted({ 'RP': 'Paroranga metodo', 'STV': 'Unuopa Transdonebla Voĉo' }.items(), key=lambda x: x[0]))

def change_election_type (index):
	global current_election_type
	current_election_type = list(election_types.items())[index][0]
	places_input.setReadOnly(current_election_type != 'STV')

def reset_form ():
	change_election_type(0)
	candidates_input.setText('')
	ignored_candidates_input.setText('')
	places_input.setValue(1)
	ballots_input.setPlainText('')

comma_regex = r'[^,\s]'
newline_regex = r'\r?\n'
def run_election ():
	candidates = re.findall(comma_regex, candidates_input.text())
	ignored_candidates = re.findall(comma_regex, ignored_candidates_input.text())
	places = places_input.value()

	ballots = re.split(newline_regex, ballots_input.toPlainText().strip())
	ballots = map(lambda b: b.strip(), ballots)
	ballots = filter(lambda b: len(b), ballots)
	ballots = list(map(lambda b: '' if b == 'blanka' else b, ballots))

	results = None
	try:
		if current_election_type == 'RP':
			results = RankedPairs(candidates, ballots, ignored_candidates)
		elif current_election_type == 'STV':
			results = STV(places, candidates, ballots, ignored_candidates)
	except TieBreakerNeededException as e:
		tie_breaker_text = 'La egalecrompanto mem enskribu sian balotilon ĉi-sube.\nEkz. A=B>C>D=E\nValidaj kandidatoj:\n%s' % (', '.join(candidates))
		tie_breaker, ok = QInputDialog.getText(window, 'Necesas egalecrompanto!', tie_breaker_text)
		if not ok:
			return
		if current_election_type == 'RP':
			results = RankedPairs(candidates, ballots, ignored_candidates, tie_breaker)
		elif current_election_type == 'STV':
			results = STV(places, candidates, ballots, ignored_candidates, tie_breaker)

	if not results:
		return

	print(results)

app = QApplication(['TEJO Voĉo'])
window = QWidget()

form = QVBoxLayout()
window.setLayout(form)

# Line 1
form_options_line1 = QHBoxLayout()
form.addLayout(form_options_line1)

# Election type picker
election_type_label = QLabel('Voĉdonsistemo:')
form_options_line1.addWidget(election_type_label)

election_type_picker = QComboBox()
form_options_line1.addWidget(election_type_picker)
election_type_picker.addItems(election_types.values())
election_type_picker.currentIndexChanged.connect(change_election_type)

# Calculate button
calculate_btn = QPushButton('Kalkuli')
form_options_line1.addWidget(calculate_btn)
calculate_btn.clicked.connect(run_election)

# Reset button
reset_btn = QPushButton('Nuligi')
form_options_line1.addWidget(reset_btn)
reset_btn.clicked.connect(reset_form)

# Line 2
form_options_line2 = QVBoxLayout()
form.addLayout(form_options_line2)

# Candidates input
candidates_label = QLabel('Voĉdonebloj: (unulitera, dividu per komo)')
form_options_line2.addWidget(candidates_label)

candidates_input = QLineEdit()
form_options_line2.addWidget(candidates_input)

# Line 3
form_options_line3 = QVBoxLayout()
form.addLayout(form_options_line3)

# Ignored candidates input
ignored_candidates_label = QLabel('Ignorataj kandidatoj: (unulitera, dividu per komo)')
form_options_line3.addWidget(ignored_candidates_label)

ignored_candidates_input = QLineEdit()
form_options_line3.addWidget(ignored_candidates_input)

# Line 4
form_options_line4 = QVBoxLayout()
form.addLayout(form_options_line4)

# Places input
places_label = QLabel('Kvanto de venkontoj: (nur por UTV)')
form_options_line4.addWidget(places_label)

places_input = QSpinBox()
form_options_line4.addWidget(places_input)
places_input.setMinimum(1)

# Line 5
form_options_line5 = QVBoxLayout()
form.addLayout(form_options_line5)

# Ballots input
ballots_label = QLabel('Balotiloj:')
form_options_line5.addWidget(ballots_label)

ballots_input = QPlainTextEdit()
form_options_line5.addWidget(ballots_input)
ballots_input.setMinimumSize(400, 500)

reset_form()

window.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.MSWindowsFixedSizeDialogHint)
window.show()
window.setFixedSize(window.size())
app.exec_()
