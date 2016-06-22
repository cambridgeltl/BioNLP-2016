////////////////////////////////////////////////////////////////////////////////
// remapStandOff.C
// first author: Takuya Matsuzaki
//
// DESCRIPTION
//  - This program adjusts the offset numbers in a stand-off file for 
//    a split text file.
//
// INPUT
//  - so file: a stand-off file
//     - a tag in the stand-off file may span across several domain regions
//      (i.e., the region [begin,end) ) of the Mapping structure.
//      But any of the start and end positions of the tags must be contained 
//      in some regions [begin,end].
//  - map file: a sequence of triples (b,e,ob)
//     - the sequence must obey the condition checkMapping(sequence) == true
//      (see the code)
//
// Ambiguity resolution
//  - start/end position of a span will be mapped so that the resulting
//   region (in the original text file) becomes shortest.
//  - empty tags are treated so that they will also be empty tags in the
//   mapped region and appear as early as possible, as long as the containment
//   relation among tags, which is specifed as the precedence order of 
//   the stand off tags, will be kept.
////////////////////////////////////////////////////////////////////////////////
#include <iostream>
#include <sstream>
#include <fstream>
#include <iterator>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <cassert>

struct Mapping {
	unsigned _begin;
	unsigned _end;
	unsigned _origBegin;

	unsigned origEnd(void) const { return _origBegin + _end - _begin; }

	unsigned adjust(unsigned n) const
	{
		assert(contain(n));
		return _origBegin + (n - _begin);
	}

	bool contain(unsigned n) const
	{
		return _begin <= n && n <= _end;
	}
};

struct CompWithEnd {
	bool operator()(const Mapping &m, unsigned n) const
	{
		return m._end < n;
	}

	bool operator()(unsigned n, const Mapping &m) const
	{
		return n < m._end;
	}
};

struct CompWithBegin {
	bool operator()(const Mapping &m, unsigned n) const
	{
		return m._begin < n;
	}

	bool operator()(unsigned n, const Mapping &m) const
	{
		return n < m._begin;
	}
};

inline
std::istream &operator>>(std::istream &ist, Mapping &m)
{
	// return (ist >> m._begin >> m._end >> m._origBegin);
	std::string line;
	if (! std::getline(ist, line)) {
		return ist;
	}

	std::istringstream iss(line);
	if (! (iss >> m._begin >> m._end >> m._origBegin)) {
		std::cerr << "Format error in the map file" << std::endl
			<< "invalid line: " << line << std::endl;
		exit(1);
	}

	return ist;
}

void printUsageAndDie(const std::string &execName)
{
	std::cerr << "Usage: " << execName << " <so-file> <map-file>"
		<< std::endl;
	exit(1);
}

bool checkMapping(const std::vector<Mapping> &ms)
{
	for (unsigned i = 0; i < ms.size(); ++i) {
		if (	ms[i]._begin <= ms[i]._end
			&& (i == 0 || ms[i - 1]._end <= ms[i]._begin)
			&& (i == 0 || ms[i - 1].origEnd() <= ms[i]._origBegin) ) {
			/// ok
		}
		else {
			return false;
		}
	}

	return true;
}

class OutOfDomainAnnotation : public std::runtime_error {
public:
	OutOfDomainAnnotation(const std::string &msg) : std::runtime_error(msg) {}
	OutOfDomainAnnotation(void)
		: std::runtime_error(
			"annotation in the outside of the clipped region") {};

	OutOfDomainAnnotation(unsigned begin, unsigned end)
		: std::runtime_error("dummy")
	{
		std::ostringstream ss;
		ss << "annotation in the outside of the clipped region" << std::endl
			<< "annotation region = [" << begin << ", " << end << ")";
		*this = OutOfDomainAnnotation(ss.str());
	}
};

typedef std::vector<Mapping>::const_iterator MItr;

std::pair<MItr, MItr> adjust(
	unsigned begin,
	unsigned end,
	const std::vector<Mapping> &mapping,
	std::pair<MItr, MItr> emptySearchRegion,
	unsigned &mbegin,
	unsigned &mend
) {
	
	std::pair<MItr, MItr> ret;
	
	if (begin == end) { /// empty tag

		MItr searchBegin = emptySearchRegion.first;
		MItr searchEnd = emptySearchRegion.second;

		MItr it = std::lower_bound(searchBegin, searchEnd, end, CompWithEnd());

		/// this empty tag is to the right of the last non-empty tag
		if (it == searchEnd) {

			it = std::lower_bound(
				searchBegin, mapping.end(), end, CompWithEnd());

			if (it == mapping.end() || ! it->contain(end)) {
				throw OutOfDomainAnnotation(begin, end);
			}
		}

		/// avoid redundant search in the case of continuous empty tags
		ret.first = it;
		ret.second = it + 1;

		mbegin = it->adjust(end);
		mend = mbegin;
	}
	else { /// non-empty tag

		MItr itBegin = std::upper_bound(
			mapping.begin(), mapping.end(), begin, CompWithBegin());

		if (itBegin == mapping.begin()) {
			throw OutOfDomainAnnotation(begin, end);
		}

		--itBegin;
		if (! itBegin->contain(begin)) {
			throw OutOfDomainAnnotation(begin, end);
		}

		MItr itEnd = std::lower_bound(
			mapping.begin(), mapping.end(), end, CompWithEnd());

		if (itEnd == mapping.end() || ! itEnd->contain(end)) {
			throw OutOfDomainAnnotation(begin, end);
		}

		ret.first = itBegin;
		ret.second = itEnd;

		mbegin = itBegin->adjust(begin);
		mend = itEnd->adjust(end);
	}

	return ret;
}

int main(int argc, char **argv)
try {
	if (argc != 3) {
		printUsageAndDie(argv[0]);
	}

	std::istream *soStream = 0;
	std::string soFileName(argv[1]);
	if (soFileName == "-") {
		soStream = &std::cin;
	}
	else {
		std::ifstream *soFile = new std::ifstream(soFileName.c_str());
		if (! *soFile) {
			throw std::runtime_error("Cannot open " + std::string(soFileName));
		}
		soStream = soFile;
	}

	std::ifstream mapFile(argv[2]);
	if (! mapFile) {
		throw std::runtime_error("Cannot open " + std::string(argv[2]));
	}

	std::vector<Mapping> mapping;
	std::copy(
		std::istream_iterator<Mapping>(mapFile),
		std::istream_iterator<Mapping>(),
		std::back_inserter(mapping));

	if (! checkMapping(mapping)) {
		throw std::runtime_error("Mapping data is corrupted");
	}

	std::pair<MItr, MItr> emptySearchRegion(mapping.begin(), mapping.end());

	std::string line;
	while (std::getline(*soStream, line)) {

		if (line.empty()) {
			continue;
		}

		std::istringstream lineIss(line);

		unsigned begin;
		unsigned end;

		if (! (lineIss >> begin >> end)) {
			throw std::runtime_error("Wrong format in the stand-off file");
		}

		std::string rest;
		if (! std::getline(lineIss, rest)) {
			throw std::runtime_error("Wrong format in the stand-off file");
		}

		unsigned mbegin;
		unsigned mend;

		emptySearchRegion
			= adjust(begin, end, mapping, emptySearchRegion, mbegin, mend);

		std::cout
			<< mbegin << '\t' << mend
			<< rest << std::endl; /// rest contains the headding '[\t ]'
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

