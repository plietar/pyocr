#!/bin/sh

run_tess()
{
	img="$1"
	shift
	out="$1"
	shift
	lang="$1"
	shift

	echo "${img} --> ${out} (${lang} / $@)"

	lang_arg=""
	if [ -n "${lang}" ]; then
		lang_arg=-l
	fi

	if ! tesseract ${img} ${out} ${lang_arg} ${lang} $@ > /dev/null 2>&1
	then
		echo "FAILED !"
	fi
}

cd tests

run_tess data/test.png tesseract/test eng
run_tess data/test.png tesseract/test eng batch.nochop makebox
run_tess data/test.png tesseract/test eng hocr
mv tesseract/test.hocr tesseract/test.words
cp tesseract/test.words tesseract/test.lines

run_tess data/test-digits.png tesseract/test-digits eng digits

run_tess data/test-european.jpg tesseract/test-european eng
run_tess data/test-european.jpg tesseract/test-european eng batch.nochop makebox
run_tess data/test-european.jpg tesseract/test-european eng hocr
mv tesseract/test-european.hocr tesseract/test-european.words
cp tesseract/test-european.words tesseract/test-european.lines

run_tess data/test-french.jpg tesseract/test-french fra
run_tess data/test-french.jpg tesseract/test-french fra batch.nochop makebox
run_tess data/test-french.jpg tesseract/test-french fra hocr
mv tesseract/test-french.hocr tesseract/test-french.words
cp tesseract/test-french.words tesseract/test-french.lines

run_tess data/test-japanese.jpg tesseract/test-japanese jpn
run_tess data/test-japanese.jpg tesseract/test-japanese jpn batch.nochop makebox
run_tess data/test-japanese.jpg tesseract/test-japanese jpn hocr
mv tesseract/test-japanese.hocr tesseract/test-japanese.words
cp tesseract/test-japanese.words tesseract/test-japanese.lines
