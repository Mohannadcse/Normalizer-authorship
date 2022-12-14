#include "ReplaceLiteral.h"
#include "RandomHelper.h"
#include "SourceTextHelper.h"
#include <sstream>

using namespace std;

void ReplaceLiteralMatchHandler::run(const MatchFinder::MatchResult &Result) {
  auto &SM = Result.Context->getSourceManager();
  auto &LO = Result.Context->getLangOpts();
  if (const auto *RS = Result.Nodes.getNodeAs<ReturnStmt>("retStmt")) {
    if (!SM.isInMainFile(RS->getLocStart()))
      return;
    // get the return value, i.e. an expression
    const auto RetValue = RS->getRetValue();

    // if the expression is an expanded macro do nothing
    /*
    if (RetValue->getLocStart().isMacroID()) {
      return;
    }


    if (const auto UO = dyn_cast<UnaryOperator>(RetValue)) {
      if (UO->getOpcode() != UnaryOperator::Opcode::UO_Minus)
        return;
    }
     */

    // the source text of the return expression
    StringRef ReturnText = getSourceText(RetValue, SM, LO);
    if (auto exp = dyn_cast<ImplicitCastExpr>(RetValue)) {
        if (auto dre = dyn_cast<DeclRefExpr>(exp->getSubExpr())) {
            if(auto ddn = dyn_cast<VarDecl>(dre->getFoundDecl())){
                std::string initvalue = getSourceText(ddn->getInit(), SM, LO);

                stringstream sstream;
                // TODO check variables in scope!

                const auto Parents = Result.Context->getParents(*RS);
                const auto Parent = Parents[0];
                // If the parent is a control statement, we need to add a compound
                // statement. Return statements are always used in functions. If the parent
                // is not a compound statement, it must be a control statement.

                if (const auto CS = Parent.get<CompoundStmt>()) {
//                    llvm::outs() << "dnn: " << *ddn->getCanonicalDecl() << "\n";
                    // If the parent is a compound statement replace the whole compound
                    // statement and declare the new variable on top.
                    sstream << "{ ";
                    for (const auto S : CS->body()) {
                        if (S == RS) {
                            sstream << "return " << initvalue << ";"
                                    << " }";
                        } else if (getSourceText(S,SM,LO) == getSourceText(ddn,SM,LO)){
                            sstream << "//" << getSourceText(S,SM,LO).str() << "\n";
                        } else {
                            sstream << getSourceText(S, SM, LO).str();
                        }
                    }
                    Replacement Replace(SM, getCharSourceRange(CS, SM, LO), sstream.str(),
                                        LO);
                    Replaces.push_back(Replace);
                } else {
                    // If the parent is a control statement replace only the return statement
                    // and introduce a new block containing the declared variable and the
                    // return statement.
                    sstream << "{"
                            << "return " << initvalue << ";"
                            << "}";
                    Replacement Replace(SM, getCharSourceRange(RS, SM, LO), sstream.str(),
                                        LO);
                    Replaces.push_back(Replace);
                }
            }
        }
    }
  }
}

void ReplaceLiteralASTConsumer::HandleTranslationUnit(ASTContext &Ctx) {
  MatchFinder Finder;
  ReplaceLiteralMatchHandler Handler;

    Finder.addMatcher(
            returnStmt(has(implicitCastExpr(has(
                    declRefExpr(to(varDecl(hasInitializer(integerLiteral()))))))),
                       unless(hasReturnValue(integerLiteral()))).bind("retStmt"), &Handler);


  Finder.matchAST(Ctx);

  auto Replaces = Handler.getReplaces();

  if (!Replaces.empty()) {
      for (auto Replace : Replaces) {
//          const auto &Replace = select_randomly(Replaces, Seed.getValue());
#ifdef MYDEBUG
          llvm::dbgs() << "Applying replacement " << Replace.toString() << "\n";
#endif
          llvm::Error Err = FileToReplaces[Replace.getFilePath()].add(Replace);
          if (Err) {
//#ifdef MYDEBUG
              llvm::errs() << "Transformation failed in " << Replace.getFilePath()
                           << "! " << llvm::toString(move(Err)) << "\n";
//#endif
//      llvm::errs() << "Code 123: No transformations possible\n";
          }
      }
  } else {
#ifdef MYDEBUG
    llvm::dbgs() << "Transformation not applicable"
                 << "\n";
#endif
    llvm::errs() << "Code 123: No transformations possible\n";
  }
}
