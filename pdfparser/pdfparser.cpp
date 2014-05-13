/* 
 *
 * This file is based on the file graphicproducer.cpp from Qadastre
 * Copyright (C) 2010 Pierre Ducroquet <pinaraf@pinaraf.info>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public License
 * along with this library; see the file COPYING.LIB.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */


/*
 * Ce programme tente de parser un fichier PDF extrait du cadastre 
 * et génère pour chaque path:
 *  - 1 ligne représentant le path au format SVG (attribut d d'un <path/>)
 *  - 1 ligne représentant son style (attribut style d'un <path/>)
 */

#include <podofo/base/PdfParser.h>
#include <podofo/base/PdfObject.h>
#include <podofo/base/PdfStream.h>

#include <QList>
#include <QStack>
#include <QPen>
#include <QBrush>
#include <QPainterPath>


#include <iostream>
#include <cstdlib>
#include <errno.h>
#include <assert.h>



class GraphicContext {
public:
    QBrush brush;
    QPen pen;
    //QPainterPath clipPath;
};


/***
 * A text representing a floating point value.
 */
class FloatText {
private:
    const char* _str;
    size_t _length;
public:
    FloatText() : _str(0), _length(0) {}
    FloatText(const char* str) {
        _str = str;
        while((*str == ' ') || (*str == '\t')) str++;
        while(((*str >= '0') && (*str <= '9')) || (*str == '.') || (*str == '-') || (*str == 'e') || (*str == 'E')) {
            str++;
        }
        _length = size_t(str - _str);
        //assert((*str == ' ') || (*str == '\t') || (*str == '\n') || (*str == '\0') || (*str == ']'));
    }
    operator std::string() const { return std::string(_str, _length); }
    size_t length() const { return _length; }
    const char* str() const { return _str; }
    double value() const { return strtod(_str, NULL); }
};

std::ostream& operator<<( std::ostream& stream, FloatText const& t )
{
        //return (stream << std::string(t));
        return stream.write(t.str(), t.length());
}


bool parseStream(const char *stream, unsigned long streamLen) {
    //std::cout << "parseStream of length " << streamLen << std::endl;
    setlocale(LC_ALL, "C");
    QStack<FloatText> stack;
    QVector<double> lastArray;
    unsigned long previousPosition = 0;
    unsigned long tokenPosition = 0;
    bool inArray = false;
    FloatText x1, y1, x2, y2, x3, y3;
    double capStyle, offset, joinStyle;
    QList<GraphicContext> contexts;
    GraphicContext currentContext;
    currentContext.brush.setStyle(Qt::SolidPattern);
    currentContext.brush.setColor(Qt::black);
    currentContext.pen.setStyle(Qt::SolidLine);
    currentContext.pen.setColor(Qt::black);
    QString currentPath;
    FloatText cur_x, cur_y;
    do {
        // Special case : array handling
        if (stream[tokenPosition] == '[') {
            inArray = true;
            tokenPosition++;
            previousPosition = tokenPosition;
            continue;
        }
        if ((stream[tokenPosition] != ' ') && (stream[tokenPosition] != '\n') && (stream[tokenPosition] != '\0') && (stream[tokenPosition] != '\t') && (stream[tokenPosition] != ']')) {
            tokenPosition++;
            continue;
        }
        if (previousPosition != tokenPosition) {
            switch (stream[previousPosition]) {
            case 'l':
                y1 = stack.pop();
                x1 = stack.pop();
                //currentPath.lineTo(x1, y1);
                std::cout << " L " << x1 << ',' << y1;
                cur_x = x1;
                cur_y = y1;
                break;
            case 'v':
                y3 = stack.pop();
                x3 = stack.pop();
                y2 = stack.pop();
                x2 = stack.pop();
                //currentPath.quadTo(x2, y2, x3, y3); WRONG, it's not a quad but a cubic command !
                std::cout << " C " << cur_x << ',' << cur_y << ' ' << x2 << ',' << y2 << ' ' << x3 << ',' << y3;
                cur_x = x3;
                cur_y = y3;
                break;
            case 'y':
                y3 = stack.pop();
                x3 = stack.pop();
                y2 = stack.pop();
                x2 = stack.pop();
                std::cout << " C " << x2 << ',' << y2 << ' ' << x3 << ',' << y3 << ' ' << x3 << ',' << y3;
                cur_x = x3;
                cur_y = y3;
                break;
            case 'm':
                y1 = stack.pop();
                x1 = stack.pop();
                //currentPath.moveTo(x1, y1);
                std::cout << " M " << x1 << ',' << y1;
                cur_x = x1;
                cur_y = y1;
                break;
            case 'h':
                //currentPath.closeSubpath();
                std::cout << " Z";
                break;
            case 'W':
                //if (currentContext.clipPath.length() == 0)
                //    currentContext.clipPath = currentPath.toPainterPath();
                //if (stream[previousPosition+1] == '*') {
                //    currentContext.clipPath.setFillRule(Qt::OddEvenFill);
                //    currentPath.setFillRule(Qt::OddEvenFill);
                //} else {
                //    currentContext.clipPath.setFillRule(Qt::WindingFill);
                //    currentPath.setFillRule(Qt::WindingFill);
                //}
                //currentContext.clipPath = currentContext.clipPath.intersected(currentPath.toPainterPath());
                break;
            case 'n':
                //currentPath = VectorPath();
                std::cout << std::endl << "" << std::endl;
                break;
            case 'q':
                contexts.append(currentContext);
                break;
            case 'Q':
                currentContext = contexts.takeLast();
                break;
            case 'S':
                //emit strikePath(currentPath, currentContext);
                //currentPath = VectorPath();
                std::cout << std::endl << "fill:none;stroke:" << currentContext.pen.color().name().toStdString();
                std::cout << ";stroke-opacity:1";
                if (currentContext.pen.style() == Qt::SolidLine) {
                    std::cout << ";stroke-dasharray:none";
                }
                std::cout << ";stroke-width:" << currentContext.pen.widthF();
                std::cout << std::endl;
                break;
            case 'w':
                currentContext.pen.setWidthF(stack.pop().value());
                break;
            case 'R':
                if (stream[previousPosition+1] == 'G') {
                    double b = stack.pop().value();
                    double g = stack.pop().value();
                    double r = stack.pop().value();
                    currentContext.pen.setColor(QColor(r*255, g*255, b*255));
                }
                break;
            case 'J':
                capStyle = stack.pop().value();
                if (capStyle == 0)
                    currentContext.pen.setCapStyle(Qt::FlatCap);
                else if (capStyle == 1)
                    currentContext.pen.setCapStyle(Qt::RoundCap);
                else
                    currentContext.pen.setCapStyle(Qt::SquareCap);
                break;
            case 'M':
                currentContext.pen.setMiterLimit(stack.pop().value());
                break;
            case 'f':
                std::cout << std::endl << "fill:" << currentContext.brush.color().name().toStdString();
                std::cout << ";stroke:none";
                if (stream[previousPosition+1] == '*')
                    //emit fillPath(currentPath, currentContext, Qt::OddEvenFill);
                    std::cout << ";fill-rule:evenodd";
                else
                    //emit fillPath(currentPath, currentContext, Qt::WindingFill);
                    std::cout << ";fill-rule:nonzero";
                //currentPath = VectorPath();
                std::cout << std::endl;
                break;
            case 'd':
                offset = stack.pop().value();
                if (lastArray.count() == 0) {
                    currentContext.pen.setStyle(Qt::SolidLine);
                } else {
                    currentContext.pen.setDashOffset(offset);
                    currentContext.pen.setDashPattern(lastArray);
                    lastArray.clear();
                }
                break;
            case 'r':
                if (stream[previousPosition+1] == 'g') {
                    double b = stack.pop().value();
                    double g = stack.pop().value();
                    double r = stack.pop().value();
                    currentContext.brush.setColor(QColor(r*255, g*255, b*255));
                }
                break;
            case 'c':
                y3 = stack.pop();
                x3 = stack.pop();
                y2 = stack.pop();
                x2 = stack.pop();
                y1 = stack.pop();
                x1 = stack.pop();
                //currentPath.cubicTo(x1, y1, x2, y2, x3, y3);
                std::cout << " C " << x1 << ',' << y1 << ' ' << x2 << ',' << y2 << ' ' << x3 << ',' << y3;
                cur_x = x3;
                cur_y = y3;
                break;
            case 'j':
                joinStyle = stack.pop().value();
                if (joinStyle  == 0)
                    currentContext.pen.setJoinStyle(Qt::MiterJoin);
                else if (joinStyle  == 1)
                    currentContext.pen.setJoinStyle(Qt::RoundJoin);
                else
                    currentContext.pen.setJoinStyle(Qt::BevelJoin);
                break;
            default:
                // handle a number then
                errno = 0;
                //double d = strtod(stream + previousPosition, NULL);
                FloatText d = FloatText(stream + previousPosition);
                if (errno != 0)
                    qFatal("Convertion to double failed !");
                if (inArray)
                    //lastArray << d;
                    lastArray << d.value();
                else
                    stack.push(d);
            }
        }
        previousPosition = tokenPosition + 1;
        if (stream[tokenPosition] == ']') {
            inArray = false;
        }
        tokenPosition++;
    } while (tokenPosition <= streamLen);
    //std::cerr << "stack: " << stack.size() << std::endl;
    return true;
}


bool parsepdf(const char* filename) {
  PoDoFo::PdfVecObjects objects;
  PoDoFo::PdfParser parser(&objects, filename);
  PoDoFo::TIVecObjects it = objects.begin();
  bool result = false;
  do {
    PoDoFo::PdfObject *obj = (*it);
#if (PODOFO_VERSION_MAJOR > 0) || (PODOFO_VERSION_MINOR > 8) || (PODOFO_VERSION_PATCH >= 3)
    if (obj->HasStream() && (obj->GetObjectLength(PoDoFo::ePdfWriteMode_Compact) > 10000)) {
#else
    if (obj->HasStream() && (obj->GetObjectLength() > 10000)) {
#endif
        PoDoFo::PdfStream *stream = obj->GetStream();
        char *buffer;
        PoDoFo::pdf_long bufferLen;
        stream->GetFilteredCopy(&buffer, &bufferLen);
        //std::cerr << "Buffer length : " << bufferLen << std::endl;
        if (bufferLen > 1000)
            result = parseStream(buffer, bufferLen);
        free(buffer);
    }
    it++;
  } while (it != objects.end());
  return result;
}

int main(int argc, char** argv) {

  if (argc != 2) {
      std::cerr << "ERROR: wrong number of argument" << std::endl;
      return -1;
  } else {
      parsepdf(argv[1]);
  }
}
