////////////////////////////////////////////////////////////////////////////////
// makeMapping.C
// first author: Takuya Matsuzaki
//
// DESCRIPTION
//  - Each line in the split text file has a corresponding line in the output,
//   in the same order as the split text file.
//  - A line in the output
//     "x y n"
//   indicates that the corresponding line in the split text spans the region 
//   [x, y) in the split text file (where x and y are byte offsets in 
//   the split text file), and it is extracted from the region
//   [ n, n + (y - x) ) in the original text file.
// 
// NOTE
//  - As is clear from the above description, we depend on the assumption
//   that a line in the split text file always has a corresponding continuous
//   region in the original file. We thus need to modify this program
//   and other parts of the system which depend on the output of this program
//   when a future version of the sentence splitter breaks the assumption.
//
////////////////////////////////////////////////////////////////////////////////
#include <iostream>
#include <string>
#include <stdexcept>
#include <fstream>
#include <sstream>
#include <cstdlib>

void printUsageAndDie(const std::string &execName)
{
	std::cerr << "Usage: " << execName << " <orig-text> <split-text>"
		<< std::endl;
	exit(1);
}

std::string errorMsgLong(
	unsigned origByte,
	char origChar,
	unsigned splitLine,
	unsigned splitByte,
	char splitChar
) {
	std::ostringstream msg;
	msg << "Split/original text do not match:" << std::endl;
	msg << "  position" << origByte << " (in bytes) in original text, "
		<< "char=\'" << origChar << "\'" << std::endl;
	msg	<< "  line " << splitLine << ", position " << splitByte
		<< " in the split-text, "
		<< "char=" << "\'" << splitChar << "\'" << std::endl;

	return msg.str();
}

int main(int argc, char **argv)
try {
	if (argc != 3) {
		printUsageAndDie(argv[0]);
	}

	std::ifstream origFile(argv[1]);
	if (! origFile) {
		throw std::runtime_error("Cannot open " + std::string(argv[1]));
	}

	std::ifstream splitFile(argv[2]);
	if (! splitFile) {
		throw std::runtime_error("Cannot open " + std::string(argv[2]));
	}

	unsigned startPos = 0;
	int origPos = 0;
	std::string line;

	unsigned lineNo = 0;

	while (std::getline(splitFile, line)) {

		++lineNo;
		
		unsigned endPos = startPos + line.size();

		unsigned origStartPos;

		if (line.size() == 0) { /// empty line
			origStartPos = origPos;
		}
		else {
			
			/// collect heading spaces
			std::string headingWs;
			for (std::string::const_iterator ch = line.begin();
					ch != line.end(); ++ch) {
				if (std::isspace(*ch)) {
					headingWs += *ch;
				}
				else {
					break;
				}
			}

			// if (line[0] == ' ') {
			//	throw std::runtime_error(
			//		"Error: Split text contains a heading space");
			// }

			/// skip newlines in the original file
			char origChar;
			while (origFile.get(origChar)) {

				++origPos;

				if (origChar != '\n') {
					origFile.unget();
					--origPos;
					break;
				}
			}

			/// collect spaces in the original file
			std::string origWs;
			while (origFile.get(origChar)) {

				++origPos;

				if (origChar == ' ' || origChar == '\t') {
					origWs += origChar;
				}
				else {
					origFile.unget();
					--origPos;
					break;
				}
			}

			#if 0
			/// skip spaces and newlines in the original file
			char origChar;
			do {
				if (! origFile.get(origChar)) {
					throw std::runtime_error(
						"Split/original text do not match");
				}
				++origPos;
			} while (origChar == ' ' || origChar == '\n');

			origFile.unget();
			--origPos;
			#endif

			/// check if the heading space part has a corresponding region
			/// in the original file
			if (origWs.size() < headingWs.size()) {
				throw std::runtime_error("Split/original text do not match");
			}

			unsigned skipLen = origWs.size() - headingWs.size();

			if (! headingWs.empty() && headingWs != origWs.substr(skipLen)) {
				throw std::runtime_error("Split/original text do not match");
			}

			origStartPos = origPos - headingWs.size();

			/// Check the identity for the rest of the line
			for (unsigned i = headingWs.size(); i < line.size(); ++i) {
				if (! origFile.get(origChar) || origChar != line[i]) {
					std::string msg = errorMsgLong(
						origPos, origChar, lineNo, i, line[i]);
					throw std::runtime_error(msg);
				}
				++origPos;
			}
		}

		std::cout << startPos << '\t' << endPos << '\t' << origStartPos
				<< std::endl;

		/// +1 to skip the new line character
		startPos = endPos + 1;
	}

	return 0;
}
catch (std::runtime_error &e)
{
	std::cerr << e.what() << std::endl;
	exit(1);
}
catch (...) {
	std::cerr << "Unknown exception" << std::endl;
	exit(1);
}
