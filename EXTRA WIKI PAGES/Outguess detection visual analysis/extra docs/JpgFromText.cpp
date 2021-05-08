#include <iostream>
#include <string.h>
#include <fstream>
#include <string>

using namespace std;

char convertToHex(char c);

int main(int argc, char *argv[]){
	
	if (argc != 4){
		cout << endl;
		cout << "*********** JpgFromText ***********" << endl << endl;
		cout << "You haven't provided all the parameters." << endl;
		cout << "The correct format is:" << endl << endl;
		cout << "\tjpgfromtext.exe [-f/-r] <input txt file> <output jpg file>" << endl << endl;
		cout << "-f - foreward direction" << endl;
		cout << "-r - reverse direction" << endl;
		return 1;
	}

	if (strcmp(argv[1], "-f") != 0 && strcmp(argv[1], "-r") != 0){
		cout << "Invalid options parameter: options are -f or -r." << endl;
		return 1;
	}

	ifstream is(argv[2]);
	ofstream os(argv[3], ofstream::binary);

	char bout = 0x00;
	char boutprev = bout;
	bool control = true;

	if (strcmp(argv[1], "-f") == 0){
		while (is.good()) {
			char b = is.get();
			b = convertToHex(b);

			if (b != (char)0xff){
				if (control) {
					bout = bout | b;
					control = false;
				}
				else {
					bout = bout << 4;
					bout = bout | b;
					os.put(bout);
					if (bout == 0xd9 && boutprev == 0xff) break;
					boutprev = bout;
					bout = 0x00;
					control = true;
				}
			}
		}
	} else {
		string data;
		while (is.good()) {
			data += is.get();
		}
		string reversed;
		string::iterator iter = data.end();
		iter -= 3;
		for (; iter != data.begin(); iter -= 2){
			string::iterator temp;
			temp = iter;
			reversed += *temp;
			temp++;
			reversed += *(temp);
		}
		
		for(string::iterator iter = reversed.begin(); iter!=reversed.end(); iter++) {
			char b = *iter;

			b = convertToHex(b);
			if (b != (char)0xff){
				if (control) {
					bout = bout | b;
					control = false;
				}
				else {
					bout = bout << 4;
					bout = bout | b;
					os.put(bout);
					if (bout == (char)0xd9 && boutprev == (char)0xff){
						is.close();
						os.close();
						return 0;
					}
					boutprev = bout;
					bout = 0x00;
					control = true;
				}
			}
		}


	}
	
	os.close();
	is.close();
	return 0;
}

char convertToHex(char c){
	char b;
	switch (c){
	case '0':b = 0x00;
		break;
	case '1':b = 0x01;
		break;
	case '2':b = 0x02;
		break;
	case '3':b = 0x03;
		break;
	case '4':b = 0x04;
		break;
	case '5':b = 0x05;
		break;
	case '6':b = 0x06;
		break;
	case '7':b = 0x07;
		break;
	case '8':b = 0x08;
		break;
	case '9':b = 0x09;
		break;
	case 'a':b = 0x0a;
		break;
	case 'b':b = 0x0b;
		break;
	case 'c':b = 0x0c;
		break;
	case 'd':b = 0x0d;
		break;
	case 'e':b = 0x0e;
		break;
	case 'f':b = 0x0f;
		break;
	default: b = 0xff;
	}

	return b;
}