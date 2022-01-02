import genanki


m1_model = genanki.Model(
  3095830070,
  'Basic (and reversed card) (genanki)',
  fields=[
    {
      'name': 'Front',
      'font': 'serif',
    },
    {
      'name': 'Back',
      'font': 'serif',
    },
    {'name': 'MyMedia'}
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Front}}',
      'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}<br>{{MyMedia}}',
    },
    {
      'name': 'Card 2',
      'qfmt': '{{Back}}<br>{{MyMedia}}',
      'afmt': '{{FrontSide}}\n\n<hr id=answer>\n\n{{Front}}',
    },
  ],
  css='.card {\n font-family: serif;\n font-size: 20px;\n text-align: center;\n color: black;\n background-color: white;\n}\n',
)

my_note = genanki.Note(
  model=m1_model,
  fields=['Capital of Argentina', 'Buenos Aires', '<img src="kotel.jpg" width=150px>'])

m1_note = genanki.Note(
  model=m1_model,
  fields=['Capital of Buffy', 'Sommerfield', '[sound:sound.mp3]'])

m2_note = genanki.Note(
  model=m1_model,
  fields=['Capital of Wojtuch', 'Pocha', '<img src="vimage.jpg" width=150px>'])

my_deck = genanki.Deck(
  2059030100,
  'Couwntry Capitalss')

my_deck.add_note(my_note)
my_deck.add_note(m1_note)
my_deck.add_note(m2_note)

my_package = genanki.Package(my_deck)
my_package.media_files = ['sound.mp3', 'kotel.jpg', 'vimage.jpg']

my_package.write_to_file('soutput.apkg')

